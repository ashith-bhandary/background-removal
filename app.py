from flask import Flask, request, after_this_request
from flask_restful import Resource, Api
import pre_process
import post_process
import model
import os, shutil

app = Flask(__name__)
api = Api(app)


class predict(Resource):
    @staticmethod
    def post():
        # try:
        # Loads the body of the event.
        input_dict = request.get_json()
        inputdata = input_dict["dataFileURL"]

        if(os.path.exists("tmp")):
            shutil.rmtree("tmp")
        os.mkdir('tmp')

        #updating the datashop job as running
        post_process.updateJob(input_dict["jobID"], "running", None)

        # running the preprocessing steps for the model. It takes dataset URL, jobID, json as input, download the dataset and read the input.
        inputPayloadForService = pre_process.run(input_dict["jobID"], inputdata["url"], inputdata["json"])

        # model buliding/ getting the predictions here. It takes jobID and inputPayloadForService as input, run the model and get precitions saved in the temp folder of lambda.
        insightsDataFileLocation = model.run(input_dict["jobID"], inputPayloadForService)

        # It takes insightsDataFileLocation, jobID as Input, upload the insights file to s3 and get the downloadable link for the same. and also send the jobID and insights link to the Datashop application.
        status_map = post_process.run(input_dict["jobID"], insightsDataFileLocation)
        print(status_map)
        return {"statusCode": status_map["status_code"], "body": status_map["json_response"]}

        # except Exception as e:
        #     #updating job with FAILED status.
        #     try:
        #         post_process.updateJob(input_dict["jobID"], None, str(e))
        #         return {"statusCode": 400, "error": str(e)}
        #     except Exception as e:
        #         return {"statusCode": 400, "error": str(e)}
        #



api.add_resource(predict, '/predict')

if __name__ == '__main__':
    app.run()


