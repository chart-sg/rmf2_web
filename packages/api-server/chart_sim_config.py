from os.path import dirname

from api_server.default_config import config

here = dirname(__file__)
run_dir = f"{here}/run"

config.update(
    {
        "db_url": "postgres://postgres:postgres@127.0.0.1:5432",
        "cache_directory": f"{run_dir}/cache",  # The directory where cached files should be stored.
        "ros_args": ["-p", "use_sim_time:=true"],
        # environment
        "demo_env": "sim",
        # robot name, fleet, charger, impt waypoints
        "environments": {
            "pudu_robot": "pudubot2",
            "pudu_fleet": "tinyRobot",
            "pudu_charger": "pudu_charger",
            "pudu_start": "pudu_charger",
            "pudu_scm": "scm",
            "temi_robot": "bed_responder",
            "temi_fleet": "tinyRobot",
            "temi_charger": "temi_charger",
            "aw_robot": "piimo_1",
            "aw_fleet": "tinyRobot",
            "aw_charger": "aw_charger",
            "aw_bed": "ward",
            "iso_bed": "bed_1",
        },
        # event driven
        "event": {"bed_exit": True, "milk_run": False, "test": True},
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
            "play_voice_wait": "http://10.233.29.219:8113/play_voice?data=please_stay_seated.wav",
            "check_aw_exit": "http://10.233.29.65:3001/check-aw-exit",
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
        },
    }
)
