import cv2 
import mediapipe as mp 
import numpy as np 
import base64 
import json 
import time 
import math 
import re 

class PalmRecognition :
    def __init__ (self ):
        self .available =True 
        self .mp_hands =mp .solutions .hands 
        self .hands =self .mp_hands .Hands (
        static_image_mode =True ,
        max_num_hands =1 ,
        min_detection_confidence =0.5 
        )

    def conversor (self ,conversor_base64 ):
        """Converte a imagem de base64 para interpretável"""
        try :
            if not conversor_base64 :
                return None 

            if ','in conversor_base64 :
                conversor_base64 =conversor_base64 .split (',')[1 ]

            conversor_base64 =re .sub (r'[^a-zA-Z0-9+/]','',conversor_base64 )
            conversor_base64 +="="*((4 -len (conversor_base64 )%4 )%4 )
            imagem_data =base64 .b64decode (conversor_base64 )
            np_array =np .frombuffer (imagem_data ,np .uint8 )
            imagem =cv2 .imdecode (np_array ,cv2 .IMREAD_COLOR )

            if imagem is None or imagem .size ==0 :
                return None 

            return imagem 
        except Exception as e :
            return None 

    def imagem_infos (self ,image_data ):
        """Captura as características da imagem"""
        imagem =self .conversor (image_data )
        if imagem is None :
            return None 

        if len (imagem .shape )!=3 or imagem .shape [0 ]<50 or imagem .shape [1 ]<50 :
            return None 

        imagem_rgb =cv2 .cvtColor (imagem ,cv2 .COLOR_BGR2RGB )
        imagem_rgb =np .ascontiguousarray (imagem_rgb )
        imagem_rgb .flags .writeable =False 

        try :
            resultados =self .hands .process (imagem_rgb )
        except Exception as e :
            return None 
        finally :
            imagem_rgb .flags .writeable =True 

        if not resultados or not resultados .multi_hand_landmarks :
            return None 

        lado_da_mao =resultados .multi_handedness [0 ].classification [0 ].label 
        referencias_da_palma =resultados .multi_hand_landmarks [0 ]
        referencias_lista =[]

        for r in referencias_da_palma .landmark :
            referencias_lista .append ({'x':r .x ,'y':r .y ,'z':r .z })

        p0 =referencias_lista [0 ]
        p5 =referencias_lista [5 ]
        p17 =referencias_lista [17 ]
        v1_x =p5 ['x']-p0 ['x']
        v1_y =p5 ['y']-p0 ['y']
        v2_x =p17 ['x']-p0 ['x']
        v2_y =p17 ['y']-p0 ['y']
        cross_z =(v1_x *v2_y )-(v1_y *v2_x )
        costas_da_mao =False 

        if lado_da_mao =='Right'and cross_z <0 :
            costas_da_mao =True 
        elif lado_da_mao =='Left'and cross_z >0 :
            costas_da_mao =True 

        if costas_da_mao :
            return json .dumps ({"error":"DORSO_DETECTADO"})

        p9 =referencias_lista [9 ]
        escala_base =math .sqrt ((p9 ['x']-p0 ['x'])**2 +(p9 ['y']-p0 ['y'])**2 )

        assinatura_geometrica =[]
        pontos_chave =[4 ,8 ,12 ,16 ,20 ]

        if escala_base >0 :


            for idx in pontos_chave :
                ponto =referencias_lista [idx ]
                distancia_ate_pulso =math .sqrt ((ponto ['x']-p0 ['x'])**2 +(ponto ['y']-p0 ['y'])**2 )
                assinatura_geometrica .append (distancia_ate_pulso /escala_base )


            for i in range (len (pontos_chave )-1 ):
                p_atual =referencias_lista [pontos_chave [i ]]
                p_prox =referencias_lista [pontos_chave [i +1 ]]
                dist_entre_dedos =math .sqrt ((p_atual ['x']-p_prox ['x'])**2 +(p_atual ['y']-p_prox ['y'])**2 )
                assinatura_geometrica .append (dist_entre_dedos /escala_base )

        template ={
        'simulated':False ,
        'timestamp':time .time (),
        'lado_da_mao':lado_da_mao ,
        'assinatura':assinatura_geometrica 
        }

        return json .dumps (template )


    def comparador_de_palmas (self ,template1 ,template2 ,threshold =0.25 ):
        """Compara a palma do Checkin com a do Checkout"""
        if not template1 or not template2 :
            return False ,0 

        try :
            t1 =json .loads (template1 )
            t2 =json .loads (template2 )

            if "error"in t1 or "error"in t2 :
                 return False ,0 

            if t1 .get ('lado_da_mao')and t2 .get ('lado_da_mao'):
                if t1 .get ('lado_da_mao')!=t2 .get ('lado_da_mao'):
                    return False ,0 

            l1 =t1 .get ('assinatura',[])
            l2 =t2 .get ('assinatura',[])


            if not l1 or not l2 or len (l1 )!=len (l2 ):
                return False ,0 

            distancias =[]
            for v1 ,v2 in zip (l1 ,l2 ):

                diferenca =abs (v1 -v2 )
                distancias .append (diferenca )

            media_distancia =sum (distancias )/len (distancias )
            match =media_distancia <threshold 
            score =1.0 -media_distancia 

            return match ,max (0 ,score )

        except Exception as e :
            return False ,0 

palm_recognition =PalmRecognition ()