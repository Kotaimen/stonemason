group "default" {
    targets = [
        "mapnik", 
        "stonemason"
    ]
}

target "mapnik" {
    context = "./docker-mapnik"
    dockerfile = "Dockerfile"
    platforms = [
        "linux/amd64", 
        "linux/arm64"
    ]
    tags = ["889515947644.dkr.ecr.us-west-2.amazonaws.com/mapnik:bionic"]
}

target "stonemason" {
    context = "."
    dockerfile = "Dockerfile"
    platforms = [
        "linux/amd64", 
        "linux/arm64"
    ]
    tags = ["889515947644.dkr.ecr.us-west-2.amazonaws.com/stonemason:0.3.3-dev"]
}
