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

        template ={
        'simulated':False ,
        'timestamp':time .time (),
        'lado_da_mao':lado_da_mao ,
        'rs':referencias_lista 
        }

        return json .dumps (template )

    def comparador_de_palmas (self ,template1 ,template2 ,threshold =0.15 ):
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

            l1 =t1 .get ('rs',[])
            l2 =t2 .get ('rs',[])

            if not l1 or not l2 :
                return False ,0 

            distancias =[]
            for p1 ,p2 in zip (l1 ,l2 ):
                dist =math .sqrt ((p1 ['x']-p2 ['x'])**2 +(p1 ['y']-p2 ['y'])**2 )
                distancias .append (dist )

            media_distancia =sum (distancias )/len (distancias )
            match =media_distancia <threshold 
            score =1.0 -media_distancia 

            return match ,max (0 ,score )

        except Exception as e :
            return False ,0 

palm_recognition =PalmRecognition ()