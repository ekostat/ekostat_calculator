# ClassificationResults

Nu uppbyggt för att hålla resultat parameter (borde vara indikator?)

Det bör antingen finnas en klass för indikatorers klassningsresultat
och en liknande för kvalitetsfaktorers klassningsresultat eller vara
en klass som fungera för båda (det senare kanske är mest lämpligt?).

## IndicatorDIN

Beräknad DIN är inget parameterobject utan self.din är None vilket gör
att den inte kommer vidare till set_data_handler eller data_filter
('NoneType' object has no attribute)

## RefValue

Jag la till add_qf_boundaries_from_file(self, qf, file_path). En sådan
def kanske ska ligga i en egen singelton klass?
Exv. QualityFactorEQRBoundaries