## To Build Docker Image. Use the command 
 docker build . -f Dockerfile.dockerfile -t "TagName"

## To Run the docker image
 docker run --rm -it "TagName"

## To push the Docker image from local system to remote repository
  docker tag optimal:v1 bhanu208/optimal:v1 <br/>
  docker push bhanu208/optimal:v1
