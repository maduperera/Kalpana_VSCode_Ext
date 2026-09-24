import torch
import torch.nn as nn
import math
from typing import Tuple

class KalpanaRIFTensor(nn.Module):
    def __init__(self, batch_size, num_heads, bands, dim, kappa=1.0, min_freq=0.1, max_freq=10.0, device='cpu'):
        super().__init__()
        self.bands = bands
        self.dim = dim
        self.kappa = kappa
        self.device = device
        
        self.state_re = torch.zeros(batch_size, num_heads, bands, dim, device=device)
        self.state_im = torch.zeros(batch_size, num_heads, bands, dim, device=device)
        
        bands_f = float(bands - 1) if bands > 1 else 1.0
        step = (max_freq - min_freq) / bands_f
        
        o3 = min_freq + torch.arange(bands, device=device).float() * step
        self.o3 = o3.view(1, 1, bands, 1)
        
        p4 = 2 * math.pi * torch.rand(bands, device=device)
        self.p4 = p4.view(1, 1, bands, 1)
        
    def write_rif(self, start_t, vector):
        batch, heads, seq_len, dim = vector.shape
        t_range = start_t + torch.arange(0, seq_len, device=self.device).float()
        
        o3_1d = self.o3.view(-1)
        p4_1d = self.p4.view(-1)
        
        angle = self.kappa * t_range.unsqueeze(1) * o3_1d.unsqueeze(0) + p4_1d.unsqueeze(0)
        cr = torch.cos(angle)
        ci = torch.sin(angle)
        
        self.state_re += torch.einsum('bhtd,tk->bhkd', vector, cr)
        self.state_im += torch.einsum('bhtd,tk->bhkd', vector, ci)
            
    def reconstruct_all(self, max_t):
        t_range = torch.arange(0, max_t, device=self.device).float()
        
        o3_1d = self.o3.view(-1)
        p4_1d = self.p4.view(-1)
        
        angle = self.kappa * t_range.unsqueeze(1) * o3_1d.unsqueeze(0) + p4_1d.unsqueeze(0)
        cr = torch.cos(angle)
        ci = torch.sin(angle)
        
        rv_re = torch.einsum('bhkd,tk->bhtd', self.state_re, cr)
        rv_im = torch.einsum('bhkd,tk->bhtd', self.state_im, ci)
        
        return (rv_re + rv_im) / self.bands


class TrueO1PhaseAttentionLayer(nn.Module):
    """
    True O(1) Phase Attention.
    Computes Softmax(Q * K^T) * V entirely in the frequency domain.
    """
    def __init__(self, embed_dim: int, num_heads: int = 8, bands: int = 2048, kappa: float = 10.0, device: str = 'cpu'):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.bands = bands
        self.kappa = kappa
        self.device = device
        
        self.K_re = torch.zeros(1, num_heads, bands, self.head_dim, device=device)
        self.K_im = torch.zeros(1, num_heads, bands, self.head_dim, device=device)
        self.V_re = torch.zeros(1, num_heads, bands, self.head_dim, device=device)
        self.V_im = torch.zeros(1, num_heads, bands, self.head_dim, device=device)
        
        min_freq, max_freq = 0.1, 10.0
        step = (max_freq - min_freq) / (bands - 1) if bands > 1 else 1.0
        self.o3 = (min_freq + torch.arange(bands, device=device).float() * step) # [bands]
        self.p4 = 2 * math.pi * torch.rand(bands, device=device) # [bands]
        
        self.current_t = 0
        self.max_cached_len = 4096
        self._init_tables(self.max_cached_len)
        
    def _init_tables(self, max_len: int = 4096):
        t_range = torch.arange(max_len, device=self.device, dtype=self.o3.dtype)
        angle = self.kappa * t_range.unsqueeze(1) * self.o3.unsqueeze(0) + self.p4.unsqueeze(0)
        self.cos_table = torch.cos(angle)
        self.sin_table = torch.sin(angle)
        self.max_cached_len = max_len

    def _ensure_dtype_device(self, x: torch.Tensor):
        if self.K_re.device != x.device or self.K_re.dtype != x.dtype:
            self.device = str(x.device)
            self.K_re = self.K_re.to(device=x.device, dtype=x.dtype)
            self.K_im = self.K_im.to(device=x.device, dtype=x.dtype)
            self.V_re = self.V_re.to(device=x.device, dtype=x.dtype)
            self.V_im = self.V_im.to(device=x.device, dtype=x.dtype)
            self.o3 = self.o3.to(device=x.device, dtype=x.dtype)
            self.p4 = self.p4.to(device=x.device, dtype=x.dtype)
            self.cos_table = self.cos_table.to(device=x.device, dtype=x.dtype)
            self.sin_table = self.sin_table.to(device=x.device, dtype=x.dtype)

    def write_kv(self, k: torch.Tensor, v: torch.Tensor):
        self._ensure_dtype_device(k)
        batch_size = k.shape[0]
        if self.K_re.shape[0] != batch_size:
            self.K_re = self.K_re.expand(batch_size, -1, -1, -1).clone()
            self.K_im = self.K_im.expand(batch_size, -1, -1, -1).clone()
            self.V_re = self.V_re.expand(batch_size, -1, -1, -1).clone()
            self.V_im = self.V_im.expand(batch_size, -1, -1, -1).clone()
            
        if self.current_t >= self.max_cached_len:
            self._init_tables(self.max_cached_len * 2)
            
        cr = self.cos_table[self.current_t].view(1, 1, self.bands, 1)
        ci = self.sin_table[self.current_t].view(1, 1, self.bands, 1)
        
        k_uns = k.unsqueeze(2)
        v_uns = v.unsqueeze(2)
        
        self.K_re += k_uns * cr
        self.K_im += k_uns * ci
        self.V_re += v_uns * cr
        self.V_im += v_uns * ci
        
        self.current_t += 1
        
    def forward(self, q: torch.Tensor, chunk_size: int = 4096) -> Tuple[torch.Tensor, torch.Tensor]:
        self._ensure_dtype_device(q)
        batch_size = q.shape[0]
        
        Z_re = torch.einsum('bhd, bhkd -> bhk', q, self.K_re)
        Z_im = torch.einsum('bhd, bhkd -> bhk', q, self.K_im)
        
        max_a = torch.full((batch_size, self.num_heads, 1), float('-inf'), device=q.device, dtype=q.dtype)
        sum_exp = torch.zeros((batch_size, self.num_heads, 1), device=q.device, dtype=q.dtype)
        
        W_re = torch.zeros(batch_size, self.num_heads, self.bands, device=q.device, dtype=q.dtype)
        W_im = torch.zeros(batch_size, self.num_heads, self.bands, device=q.device, dtype=q.dtype)
        
        for start_t in range(0, self.current_t, chunk_size):
            end_t = min(start_t + chunk_size, self.current_t)
            
            cr = self.cos_table[start_t:end_t]
            ci = self.sin_table[start_t:end_t]
            
            a_chunk = torch.einsum('bhk, tk -> bht', Z_re, cr) + torch.einsum('bhk, tk -> bht', Z_im, ci)
            a_chunk = (a_chunk / self.bands) / math.sqrt(self.head_dim)
            
            chunk_max = torch.max(a_chunk, dim=-1, keepdim=True)[0]
            new_max = torch.maximum(max_a, chunk_max)
            
            scale = torch.exp(max_a - new_max)
            W_re = W_re * scale
            W_im = W_im * scale
            sum_exp = sum_exp * scale
            
            exp_a = torch.exp(a_chunk - new_max)
            sum_exp = sum_exp + torch.sum(exp_a, dim=-1, keepdim=True)
            
            W_re = W_re + torch.einsum('bht, tk -> bhk', exp_a, cr)
            W_im = W_im + torch.einsum('bht, tk -> bhk', exp_a, -ci)
            
            max_a = new_max
            
        if self.current_t > 0:
            W_re = W_re / sum_exp
            W_im = W_im / sum_exp
        
        out_re = torch.einsum('bhkd, bhk -> bhd', self.V_re, W_re)
        out_im = torch.einsum('bhkd, bhk -> bhd', self.V_im, W_im)
        
        out = (out_re - out_im) / self.bands
        
        dummy_weights = torch.empty(0, device=q.device, dtype=q.dtype)
        return out, dummy_weights
