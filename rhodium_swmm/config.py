from __future__ import absolute_import, division, print_function

from platypus.config import PlatypusConfig

class _RhodiumSwmmConfig(object):
    
    def __init__(self):
        super(_RhodiumSwmmConfig, self).__init__()
        self.initialize = None
        self.parallel_initialize = None
     
    @property
    def default_evaluator(self):
        return PlatypusConfig.default_evaluator
     
    @default_evaluator.setter
    def default_evaluator(self, value):
        PlatypusConfig.default_evaluator = value
        
    @property
    def default_log_frequency(self):
        return PlatypusConfig.default_log_frequency
    
    @default_log_frequency.setter
    def default_log_frequency(self, value):
        PlatypusConfig.default_log_frequency = value
        
RhodiumSwmmConfig = _RhodiumSwmmConfig()
