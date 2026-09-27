from transformers import Cache
from .core import KalpanaEngineTensor

class KalpanaCache(Cache):
    """
    Overrides the default O(N) HuggingFace DynamicCache with the O(1) Kalpanā RIF!
    """
    def __init__(self, config=None, batch_size=1, device='cpu', bandwidth=2048, **kwargs):
        bandwidth = kwargs.get('bandwidth', kwargs.get('bands', bandwidth))
        batch_size = kwargs.get('batch_size', kwargs.get('batch', batch_size))
        
        if config is not None:
            self.num_layers = getattr(config, "num_hidden_layers", getattr(config, "n_layer", 32))
            self.num_key_value_heads = getattr(config, "num_key_value_heads", getattr(config, "num_attention_heads", getattr(config, "n_head", 8)))
            
            if hasattr(config, "head_dim"):
                self.head_dim = config.head_dim
            else:
                hidden_size = getattr(config, "hidden_size", 4096)
                num_attention_heads = getattr(config, "num_attention_heads", getattr(config, "n_head", 32))
                self.head_dim = hidden_size // num_attention_heads
        else:
            self.num_layers = kwargs.get('num_layers', 32)
            self.num_key_value_heads = kwargs.get('num_key_value_heads', kwargs.get('heads', 8))
            self.head_dim = kwargs.get('head_dim', kwargs.get('dimensions', kwargs.get('dimension', kwargs.get('dim', 128))))
            
        self.device = device
        self.seen_tokens = [0] * self.num_layers
        self.bandwidth = bandwidth
        
        self.layers = []
        self.key_cache = []
        self.value_cache = []
        
        self.key_rifs = [
            KalpanaEngineTensor(
                batch_size=batch_size, 
                num_heads=self.num_key_value_heads, 
                bandwidth=bandwidth, 
                dim=self.head_dim, 
                device=device
            ) for _ in range(self.num_layers)
        ]
        self.val_rifs = [
            KalpanaEngineTensor(
                batch_size=batch_size, 
                num_heads=self.num_key_value_heads, 
                bandwidth=bandwidth, 
                dim=self.head_dim, 
                device=device
            ) for _ in range(self.num_layers)
        ]

    @property
    def is_compileable(self):
        return False
        
    def update(self, key_states, value_states, layer_idx, cache_kwargs=None):
        seq_len = key_states.shape[2]
        current_t = self.seen_tokens[layer_idx]
        
        self.key_rifs[layer_idx].write_rif(current_t, key_states)
        self.val_rifs[layer_idx].write_rif(current_t, value_states)
        
        self.seen_tokens[layer_idx] += seq_len
        
        full_keys = self.key_rifs[layer_idx].reconstruct_all(self.seen_tokens[layer_idx]).to(key_states.dtype)
        full_vals = self.val_rifs[layer_idx].reconstruct_all(self.seen_tokens[layer_idx]).to(value_states.dtype)
        
        return full_keys, full_vals
        
    def get_seq_length(self, layer_idx=0):
        return self.seen_tokens[layer_idx]
        
    def get_max_length(self):
        return None

KalpanaHuggingFaceCache = KalpanaCache
