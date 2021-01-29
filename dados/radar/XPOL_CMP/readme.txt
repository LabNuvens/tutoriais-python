Informa��es sobre o radar Banda-X:

Resolucao angular: 1 grau
Resolucao radial: 200 m
Numero de elevacoes: 17
PRF: 1500/1200 Hz, stagger de 5/4 (12 primeiras eleva��es), 1500 Hz (restantes)
Velocidade da antena: 12 graus/s (12 primeiras elevacoes), depois 26
Angulos de elevacao: 0.5, 1.8, 3.1, 4.4, 5.7, 7.0, 8.3, 9.6, 10.9, 13.0, 15.0, 18.0, 22.0, 26.0, 32.0, 40.0, 55.0
lon = -47.056153
lat = -22.813893
altitude = 680 m
comprimento de onda = 0.03202 m
largura de feixe = 1.3 grau 

level_0:

Dados volum�tricos (dBZ, dBuZ, V, W, ZDR, uPhiDP, PhiDP, KDP, RhoHV)

level_1:

Dados volum�tricos com corre��o de atenua��o (dBZ, ZDR) calculada atrav�s do m�todo ZPHI. Mais detalhes consultar o arquivo atten_corr.pdf

level_2:

Precipita��o a 3 km de altura (pseudo-CAPPI - Mais detalhes consultar o arquivo cappi_alg.pdf). As taxas de precipita��o s�o calculadas com rela��o Marshall-Palmer (diret�rio Z_R) e com dupla-polariza��o (diret�rio KDP_R). 

Formato do arquivo: Float, 4-bytes, 1000x1000, sem cabe�alho. Um exemplo de uma imagem gerada com o arquivo

level_2/rain_rates/KDP_R/rain_xband_kdp_orig/2016-12-03/rain_xband_kdp_orig_201612031940.bin.gz

encontra-se em exemplo_117BRX_2016120319400.png

Cantos da matriz: 

lat_inf_direita="-23.7102"
lat_sup_esquerda="-21.9117"
lon_inf_direita="-46.074"
lon_sup_esquerda="-48.0255"

Coeficientes para o c�lculo de taxa de precipita��o:

Z = aR^b (Marshall-Palmer)
R = c|KDP|^d

a = 200.0
b = 1.6
c = 19.63
d = 0.823

Mais detalhes consultar o arquivo rain_alg.pdf
