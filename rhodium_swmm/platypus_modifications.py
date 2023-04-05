from platypus import SubmitEvaluator, LOGGER, NSGAII, RandomGenerator, TournamentSelector
import logging
import multiprocessing as mp

class ProcessPoolEvaluatorWithInit(SubmitEvaluator):
    
    def __init__(self, processes=None, initializer=None, initargs=()):
        try:
            from concurrent.futures import ProcessPoolExecutor
            self.executor = ProcessPoolExecutor(max_workers=processes, initializer=initializer, mp_context=mp.get_context('spawn'), initargs=initargs)
            super(ProcessPoolEvaluatorWithInit, self).__init__(self.executor.submit)
            LOGGER.log(logging.INFO, "Started process pool evaluator")
            
            if processes:
                LOGGER.log(logging.INFO, "Using user-defined number of processes: %d", processes)
        except ImportError:
            # prevent error from showing in Eclipse if concurrent.futures not available
            raise
        
    def close(self):
        LOGGER.log(logging.DEBUG, "Closing process pool evaluator")
        self.executor.shutdown()

class NSGAII_mod(NSGAII):
    
    def __init__(self, problem,
                 population_size = 100,
                 generator = RandomGenerator(),
                 selector = TournamentSelector(2),
                 variator = None,
                 archive = None,
                 **kwargs):
        super(NSGAII_mod, self).__init__(problem=problem, population_size=population_size, generator=generator, selector=selector, variator=variator, archive=archive, **kwargs)

        self.all_results = []
        
    def step(self):
        if self.nfe == 0:
            self.initialize()
        else:
            self.iterate()
            
        self.all_results.extend(self.population)

        if self.archive is not None:
            self.result = self.archive
        else:
            self.result = self.population