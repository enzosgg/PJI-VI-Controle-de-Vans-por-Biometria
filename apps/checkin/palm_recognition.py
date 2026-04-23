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

    def _decode_base64 (self ,base64_string ):
        try :
            if not base64_string :
                return None 

            if ','in base64_string :
                base64_string =base64_string .split (',')[1 ]

            base64_string =re .sub (r'[^a-zA-Z0-9+/]','',base64_string )

            base64_string +="="*((4 -len (base64_string )%4 )%4 )

            img_data =base64 .b64decode (base64_string )

            np_arr =np .frombuffer (img_data ,np .uint8 )

            img =cv2 .imdecode (np_arr ,cv2 .IMREAD_COLOR )

            if img is None or img .size ==0 :
                return None 

            return img 
        except Exception as e :
            return None 

    def extract_features (self ,image_data ):
        img =self ._decode_base64 (image_data )
        if img is None :
            return None 

        if len (img .shape )!=3 or img .shape [0 ]<50 or img .shape [1 ]<50 :
            return None 

        img_rgb =cv2 .cvtColor (img ,cv2 .COLOR_BGR2RGB )

        img_rgb =np .ascontiguousarray (img_rgb )

        img_rgb .flags .writeable =False 

        try :
            results =self .hands .process (img_rgb )
        except Exception as e :
            return None 
        finally :
            img_rgb .flags .writeable =True 

        if not results or not results .multi_hand_landmarks :
            return None 

        landmarks_list =[]
        for hand_landmarks in results .multi_hand_landmarks :
            for landmark in hand_landmarks .landmark :
                landmarks_list .append ({'x':landmark .x ,'y':landmark .y ,'z':landmark .z })

        template ={
        'simulated':False ,
        'timestamp':time .time (),
        'landmarks':landmarks_list 
        }
        return json .dumps (template )

    def compare_templates (self ,template1 ,template2 ,threshold =0.15 ):
        if not template1 or not template2 :
            return False ,0 

        try :
            t1 =json .loads (template1 )
            t2 =json .loads (template2 )

            l1 =t1 .get ('landmarks',[])
            l2 =t2 .get ('landmarks',[])

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