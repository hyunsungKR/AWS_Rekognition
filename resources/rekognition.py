from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token,jwt_required,get_jwt
from flask_jwt_extended import create_access_token,jwt_required,get_jwt
from mysql.connector import Error
from mysql_connection import get_connection
from datetime import datetime
import boto3
from config import Config

class ObjectDetectionResource(Resource) :
    
    # S3에 저장되어있는 이미지를
    # 객체 탐지하는 API
    
    def get(self) :

        # 1. 클라이언트로부터 파일명을 받아온다.
        filename = request.args.get('filename')
        # 2. 위의 파일은 이미 S3에 있는 상황
        # 따라서 AWS의 Rekognition 인공지능 서비스를 이용해서
        # Object detection한다.


        # 리코그니션 서비스를 이용할 수 있는지
        # IAM의 유저 권한 확인하고 설정해준다.
        client=boto3.client('rekognition',
                    'ap-northeast-2',
                    aws_access_key_id=Config.ACCESS_KEY,
                    aws_secret_access_key=Config.SECRET_ACCESS)
        response=client.detect_labels(Image={'S3Object':{'Bucket':Config.S3_BUCKET,'Name':filename}},
                            MaxLabels= 10 )

        print(response['Labels'][0])

        for label in response['Labels']:
            print ("Label: " + label['Name'])
            print ("Confidence: " + str(label['Confidence']))
            print ("Instances:")
            for instance in label['Instances']:
                print ("  Bounding box")
                print ("    Top: " + str(instance['BoundingBox']['Top']))
                print ("    Left: " + str(instance['BoundingBox']['Left']))
                print ("    Width: " +  str(instance['BoundingBox']['Width']))
                print ("    Height: " +  str(instance['BoundingBox']['Height']))
                print ("  Confidence: " + str(instance['Confidence']))
                print()
                print ("Parents:")
                for parent in label['Parents']:
                    print ("   " + parent['Name'])
                    print ("----------")
                    print ()
        return {'result':'success','Labels':response['Labels']},200


class PhotoRekognitionResource(Resource) :
    def post(self) :
        
        if 'photo' not in request.files :
            return {'error':'파일 업로드 하세요'},400

        file = request.files['photo']

        # 클라이언트가 보낸 파일의 파일명을
        # 변경시켜서 S3에 올려야 유니크하게 
        # 파일을 관리할 수 있다.

        # 파일명을 유니크하게 만드는 방법
        current_time=datetime.now()
        new_file_name=current_time.isoformat().replace(':','_') + '.jpg'

        print(new_file_name)

        # 파일명을, 유니크한 이름으로 변경한다.
        # 클라이언트에서 보낸 파일명을 대체!

        file.filename = new_file_name

        # S3에 파일을 업로드하면 된다.
        # S3에 파일 업로드하는 라이브러리가 필요
        # boto3 라이브러리를 이용해서 업로드한다.
        # 참고 : 라이브러리 설치는 pip install boto3

        client=boto3.client('s3',
                    aws_access_key_id = Config.ACCESS_KEY ,
                    aws_secret_access_key = Config.SECRET_ACCESS)
        
        try :
            client.upload_fileobj(file,Config.S3_BUCKET,new_file_name,
                                    ExtraArgs ={'ACL':'public-read','ContentType':file.content_type})
        
        except Exception as e :
            return {'error':str(e)}, 500

        # 리코그니션 서비스를 이용할 수 있는지
        # IAM의 유저 권한 확인하고 설정해준다.
        client=boto3.client('rekognition',
                    'ap-northeast-2',
                    aws_access_key_id=Config.ACCESS_KEY,
                    aws_secret_access_key=Config.SECRET_ACCESS)
        response=client.detect_labels(Image={'S3Object':{'Bucket':Config.S3_BUCKET,'Name':new_file_name}},
                            MaxLabels= 10 )

        # 내가 돌린 for 문
        # num=np.arange(0,9+1)
        # print(response['Labels'][0]['Name'])
        # print(num)
        # labels = []
        # for x in num :
        #     labels.append(response['Labels'][x]['Name'])
        
        textDetections=response['TextDetections']
        print ('Detected text\n----------')
        for text in textDetections:
                print ('Detected text:' + text['DetectedText'])
                print ('Confidence: ' + "{:.2f}".format(text['Confidence']) + "%")
                print ('Id: {}'.format(text['Id']))
                if 'ParentId' in text:
                    print ('Parent Id: {}'.format(text['ParentId']))
                print ('Type:' + text['Type'])
                print()

        

        # 위의 response에서 필요한 데이터만 가져와서
        # 클라이언트에게 보내준다
        # labels : [  ]


        return {'result':'success','labels':textDetections},200