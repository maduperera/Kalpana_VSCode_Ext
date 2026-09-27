import torch
import torch.nn as nn
import math

class KalpanaEngineTensor(nn.Module):
    """
    Kalpanā Resonant Interference Field (RIF) Memory Engine
    Maintains an O(1) memory footprint for storing an infinite stream of vectors.
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        
        shape = kwargs.get('shape', None)
        bandwidth = kwargs.get('bandwidth', kwargs.get('bands', 2048))
        kappa = kwargs.get('kappa', 1.0)
        min_freq = kwargs.get('min_freq', 0.1)
        max_freq = kwargs.get('max_freq', 10.0)
        device = kwargs.get('device', 'cpu')
        
        batch_size = 1
        num_heads = 8
        dim = 128
        
        if len(args) > 0:
            if isinstance(args[0], (tuple, list)):
                shape = args[0]
                if len(args) > 1:
                    bandwidth = args[1]
            else:
                if len(args) == 4:
                    batch_size, num_heads, bandwidth, dim = args
                elif len(args) == 3:
                    batch_size, num_heads, dim = args
                else:
                    batch_size = args[0] if len(args) > 0 else 1
                    num_heads = args[1] if len(args) > 1 else 8
                    bandwidth = args[2] if len(args) > 2 else 2048
                    dim = args[3] if len(args) > 3 else 128
        else:
            if shape is not None:
                batch_size = shape[0]
                num_heads = shape[1]
                dim = shape[2]
            else:
                batch_size = kwargs.get('batch_size', kwargs.get('batch', 1))
                num_heads = kwargs.get('num_heads', kwargs.get('heads', 8))
                dim = kwargs.get('dim', kwargs.get('dimensions', kwargs.get('dimension', 128)))
                
        self.batch_size = batch_size
        self.num_heads = num_heads
        self.bands = bandwidth
        self.dim = dim
        self.kappa = kappa
        self.device = device
        self.current_t = 0
        
        self.state_re = torch.zeros(batch_size, num_heads, bandwidth, dim, device=device)
        self.state_im = torch.zeros(batch_size, num_heads, bandwidth, dim, device=device)
        
        self.state_re_v = torch.zeros(batch_size, num_heads, bandwidth, dim, device=device)
        self.state_im_v = torch.zeros(batch_size, num_heads, bandwidth, dim, device=device)
        self._is_dual = False
        
        bands_f = float(bandwidth - 1) if bandwidth > 1 else 1.0
        step = (max_freq - min_freq) / bands_f
        
        o3 = min_freq + torch.arange(bandwidth, device=device).float() * step
        self.o3 = o3.view(1, 1, bandwidth, 1)
        
        p4 = 2 * math.pi * torch.rand(bandwidth, device=device)
        self.p4 = p4.view(1, 1, bandwidth, 1)
        
    def write_rif(self, start_t, vector, is_value=False):
        batch, heads, seq_len, dim = vector.shape
        chunk = 128
        for i in range(0, seq_len, chunk):
            end_i = min(i + chunk, seq_len)
            c_len = end_i - i
            t = start_t + i + torch.arange(c_len, device=self.device).float()
            
            angle = self.kappa * self.o3.unsqueeze(2) * t.view(1, 1, -1, 1, 1) + self.p4.unsqueeze(2)
            v = vector[:, :, i:end_i, :].unsqueeze(3)
            
            if is_value:
                self.state_re_v += (v * torch.cos(angle)).sum(dim=2)
                self.state_im_v += (v * torch.sin(angle)).sum(dim=2)
                self._is_dual = True
            else:
                self.state_re += (v * torch.cos(angle)).sum(dim=2)
                self.state_im += (v * torch.sin(angle)).sum(dim=2)
                
    def reconstruct_all(self, max_t, is_value=False):
        t_range = torch.arange(0, max_t, device=self.device).float()
        angle = self.kappa * self.o3 * t_range.view(-1, 1, 1, 1, 1) + self.p4
        cr = torch.cos(angle)
        ci = torch.sin(angle)
        
        state_re = self.state_re_v if is_value else self.state_re
        state_im = self.state_im_v if is_value else self.state_im
        
        rv = state_re * cr + state_im * ci
        return rv.mean(dim=3).permute(1, 2, 0, 3)
        
    def update(self, key, value=None):
        if len(key.shape) == 3:
            key_unsqueezed = key.unsqueeze(2)
        else:
            key_unsqueezed = key
            
        if value is not None:
            if len(value.shape) == 3:
                value_unsqueezed = value.unsqueeze(2)
            else:
                value_unsqueezed = value
                
            self.write_rif(self.current_t, key_unsqueezed, is_value=False)
            self.write_rif(self.current_t, value_unsqueezed, is_value=True)
            self.current_t += key_unsqueezed.shape[2]
        else:
            self.write_rif(self.current_t, key_unsqueezed, is_value=False)
            self.current_t += key_unsqueezed.shape[2]
            
    def retrieve(self, t=None):
        max_t = t if t is not None else self.current_t
        if max_t == 0:
            k_shape = (self.batch_size, self.num_heads, 0, self.dim)
            if self._is_dual:
                return torch.zeros(k_shape, device=self.device), torch.zeros(k_shape, device=self.device)
            return torch.zeros(k_shape, device=self.device)
            
        recon_k = self.reconstruct_all(max_t, is_value=False)
        if self._is_dual:
            recon_v = self.reconstruct_all(max_t, is_value=True)
            return recon_k.squeeze(2), recon_v.squeeze(2)
        return recon_k.squeeze(2)

KalpanaRIFTensor = KalpanaEngineTensor
