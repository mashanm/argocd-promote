import yaml
import base64
from github import Github
from github import Auth
import logging.config
import os

DEFAULT_CONFIG_PATH = os.path.dirname(__file__) + "/conf"
LOG_CONFIG = DEFAULT_CONFIG_PATH + "/logging_config.yaml"
valuesRepo = "trimble-oss/helm-values"
defaultBranch = "main"


def setup_logger():
    with open(LOG_CONFIG, "r") as config_file:
        logging.config.dictConfig(yaml.safe_load(config_file.read()))


def ghclient(token: str) -> Github():
    logging.debug("set up github client")
    return Github(auth=Auth.Token(token))


def get_file(client: Github(), filepath: str, valuesrepo: str = valuesRepo,
             branch: str = defaultBranch) -> tuple[any, any]:
    logging.debug("set up repo object for repo {repo}".format(repo=valuesRepo))
    repo = client.get_repo(valuesrepo)
    logging.debug("repo = {repo}".format(repo=str(repo)))
    valuesfile = repo.get_contents(filepath, ref=branch)
    logging.debug("encoded file = {file}".format(file=valuesfile))
    return repo, valuesfile


def get_filepath(service: str, environment: str) -> str:
    logging.debug(
        "set filepath as {service}/{environment}/values.yaml".format(service=service, environment=environment))
    return "{service}/{environment}/values.yaml".format(service=service, environment=environment)


def update_values_yaml(client: Github(), service: str, image_tag: str, environment: str,
                       branch: str = defaultBranch, createpull: bool = False) -> any:
    filepath = get_filepath(service, environment)
    commitmsg = "updating image tag {image_tag} for {service}/{environment}".format(image_tag=image_tag,
                                                                                    service=service,
                                                                                    environment=environment)
    logging.debug("commit message = {msg}".format(msg=commitmsg))
    repo, file = get_file(client, filepath, branch=branch)
    valuesyaml = yaml.safe_load(base64.b64decode(file.content))
    logging.debug("set image tag as {image_tag}".format(image_tag=image_tag))
    valuesyaml["image"]["tag"] = image_tag  # set image tag
    if environment == "production":
        createpull = True
    if not createpull:
        logging.info("updating image tag {image_tag} on branch {branch} for service {service}".format(
            image_tag=image_tag, branch=branch, service=service))
        return repo.update_file(file.path, commitmsg, yaml.safe_dump(valuesyaml), file.sha, branch=branch)
    else:
        import random
        target_branch = "{service}/{environment}/{randint}".format(service=service, environment=environment,
                                                                   randint=str(random.randint(1000, 9999))).replace("/",
                                                                                                                    "-")
        sb = repo.get_branch(branch)
        repo.create_git_ref(ref='refs/heads/' + target_branch, sha=sb.commit.sha)
        repo.update_file(file.path, commitmsg, yaml.safe_dump(valuesyaml), file.sha,
                         branch=target_branch)
        logging.info("creating pr to branch {branch} for service {service}".format(service=service, branch=branch))
        repo.create_pull(title="{service} {environment} release".format(service=service, environment=environment),
                         body=commitmsg, head=target_branch, base=branch)


def get_image_tag(client, service, environment, branch) -> str:
    filepath = get_filepath(service, environment)
    _, file = get_file(client, filepath, branch=branch)
    valuesyaml = yaml.safe_load(base64.b64decode(file.content))
    logging.debug("image tag = {image_tag}".format(image_tag=valuesyaml["image"]["tag"]))
    return valuesyaml["image"]["tag"]
