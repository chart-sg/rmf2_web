# pylint: disable=line-too-long
config = {
    # ip or hostname to bind the socket to, this only applies when running the server in
    # standalone mode.
    # "host": "127.0.0.1",
    "host": "0.0.0.0",
    # port to bind to, this only applies when running the server in standalone mode.
    "port": 8000,
    # "db_url": "sqlite://:memory:",
    # url that rmf-server is being served on.
    # When being a proxy, this must be the url that rmf-server is mounted on.
    # E.g. https://example.com/rmf/api/v1
    "public_url": "http://10.233.29.66:8000",
    # "public_url": "http://localhost:8000",
    "cache_directory": "run/cache",  # The directory where cached files should be stored.
    "log_level": "INFO",  # https://docs.python.org/3.8/library/logging.html#levels
    # a user that is automatically given admin privileges, note that this does not guarantee that the user exists in the identity provider.
    "builtin_admin": "admin",
    # path to a PEM encoded RSA public key which is used to verify JWT tokens, if the path is relative, it is based on the working dir.
    "jwt_public_key": None,
    # url to the oidc endpoint, used to authenticate rest requests, it should point to the well known endpoint, e.g.
    # http://localhost:8080/auth/realms/rmf-web/.well-known/openid-configuration.
    # NOTE: This is ONLY used for documentation purposes, the "jwt_public_key" will be the
    # only key used to verify a token.
    "oidc_url": None,
    # Audience the access token is meant for. Can also be an array.
    # Used to verify the "aud" claim.
    "aud": "rmf_api_server",
    # url or string that identifies the entity that issued the jwt token
    # Used to verify the "iss" claim
    # If iss is set to None, it means that authentication should be disabled
    "iss": None,
    # list of arguments passed to the ros node, "--ros-args" is automatically prepended to the list.
    # e.g.
    #   Run with sim time: ["-p", "use_sim_time:=true"]
    # "ros_args": [],
    # "ros_args": ["-p", "use_sim_time:=true"],
    "ros_args": ["-p", "use_sim_time:=false"],
    # sim OR chart
    "demo_env": "chart",
    "environments": {
        "sim": {
            "pudu_robot": "pudubot2",
            "pudu_fleet": "tinyRobot",
            "pudu_charger": "pudu_charger",
            "pudu_start": "pudu_charger",
            "temi_robot": "bed_responder",
            "temi_fleet": "tinyRobot",
            "temi_charger": "temi_charger",
            "aw_robot": "piimo_1",
            "aw_fleet": "tinyRobot",
            "aw_charger": "aw_charger",
            "iso_bed": "bed_1",
        },
        "chart": {
            "pudu_robot": "pudubot2",
            "pudu_fleet": "pudubot2",
            "pudu_charger": "standby",
            # "pudu_charger": "blanki_charger",
            "pudu_start": "blanki_start",
            "temi_robot": "bed_responder",
            "temi_fleet": "Temi",
            "temi_charger": "temi_charger",
            "aw_robot": "piimo_1",
            "aw_fleet": "piimo",
            "aw_charger": "piimo_charger",
            "iso_bed": "bed_2",
        },
    },
    # event driven
    "event": {"bed_exit": True, "milk_run": True, "mqtt": False},
    # temi configs
    "temi": {
        "temi_id": "00119140017",
        "video_sequence": "666a69864780787af86c8e5c",
        "bed_exit_sequence": "64a39c872e9477138cdd2e8e",
    },
    # aw configs
    "aw": {
        "moving_off_long": "foo.wav",
        "moving_off_short": "foo.wav",
        "host_url": "http://10.233.29.240:8113/",
        "check_aw_exit": "http://10.233.29.65:3001/check-aw-exit",
        # "check_aw_exit": "https://jsonplaceholder.typicode.com/posts",
        "voice_endp": "64a39c872e9477138cdd2e8e",
        "get_buckle_endp": "http://10.233.29.84:3001/check-aw-exit",
        "play_voice_endp": "http://10.233.29.84:8113/play_voice?data=foo.wav",
    },
    # delay config
    "delays": {
        "milk_run": 5,
        "delivery": 15,
        "aw_end": 30,
        "orientation_video": 60,
        "responder_delay": 1,
    }
    # auth using openid keycloak
    # "jwt_public_key": "/home/asraf/rmf2_web/packages/api-server/api_server/rmf.pem",
    # "oidc_url": "https://keycloak.ctfportal.com/auth/realms/rmf-web/.well-known/openid-configuration",
    # "aud": "account",
    # "iss": "https://keycloak.ctfportal.com/auth/realms/rmf-web",
}
