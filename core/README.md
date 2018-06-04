##Dependencies
pandas 0.19
för att konvertera raddata till kolumndata används df.stack(). bugg som påverkar df.stack() i pandas >0.19.2. Därför bör vi hålla oss till version 0.19.2 ist�llet för 0.20.x
För mer info kring bugg:
- https://github.com/pandas-dev/pandas/issues/16323
- https://github.com/pandas-dev/pandas/pull/16325
- https://github.com/pandas-dev/pandas/issues/16925
(   DataHandler: Vid omformatering av data används df.stack()   )
