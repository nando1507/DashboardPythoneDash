Select * from TbCoronaVirusBrasil With (nolock) where Municipio is null and PopulacaoTCU2019 != 0 
and data = '2021-09-14'
and estado is not null