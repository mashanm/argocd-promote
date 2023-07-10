#!/usr/bin/env python3
import argparse
import os

from gitops import *

if __name__ == "__main__":
    setup_logger()
    parser = argparse.ArgumentParser(description='script to promote image tags in k8s values ')
    parser.add_argument('--service', '-s', help='service name',
                        required=True, default=os.getenv("INPUT_SERVICE", None))
    parser.add_argument(
        '--image-tag', '-v', help='version tag of image for deployment',
        default=os.getenv("INPUT_IMAGE_TAG", None), required=False
    )
    parser.add_argument(
        '--from-env',
        '-F',
        help='environment to fetch the image tag',
        required=False,
        default=os.getenv("INPUT_FROMENV", None),
    )
    parser.add_argument(
        '--environment', '-e', help='environment name to update',
        default=os.getenv("INPUT_ENVIRONMENT", None), required=True
    )
    parser.add_argument(
        '--token', '-t', help='github access token to use', required=True, default=os.getenv("INPUT_ACCESS_TOKEN", None)
    )
    parser.add_argument(
        '--branch', '-b', help='branch to push the new image tag, defaults to main', required=False,
        default=os.getenv("INPUT_BRANCH", None)
    )
    parser.add_argument(
        '--create-pr', '-pr', help='flag to create PR', default=False, required=False,
        action=argparse.BooleanOptionalAction
    )
    args = parser.parse_args()
    token = args.token
    branch = args.branch
    create_pr = args.create_pr
    if token is None or token == "":
        token = os.getenv("DEPLOYMENT_TOKEN", "")
        if token == "":
            logging.error("token cannot be empty")
            raise "token cannot be empty"
    client = ghclient(token)

    if branch is None:
        logging.info("set up main branch as default branch")
        branch = "main"

    if os.getenv("INPUT_CREATEPR", False) and os.getenv("INPUT_CREATEPR").lower() == "true":
        create_pr = True

    if args.from_env is None:
        if args.image_tag is not None:
            update_values_yaml(client, args.service, args.image_tag, args.environment, branch, create_pr)
        else:
            logging.error("image-tag or from-env should be passed as input")
            raise "image-tag or from-env should be passed as input"
    else:
        image_tag = get_image_tag(client, args.service, args.from_env, branch)
        update_values_yaml(client, args.service, image_tag, args.environment, branch, create_pr)
