import asyncio

hwaccel_opts = {
    "sw": {
        "decode": [],
        "encode": [
            "-c:v", "libx264",
            "-preset": "ultrafast"
        ],
        "scale": [
            "-vf","scale=w={w}:h={h}",
            "-sws_flags", "neighbor",
            "-pix_fmt", "{fmt}"
       ]
    },
    "nv": {
        "decode": [
            "-hwaccel", "nvdec",
            "-hwaccel_output_format", "cuda",
        ],
        "encode": [
            "-c:v","h264_nvenc",
            "-preset","fast"
        ],
        "scale": [
            "-vf","scale_cuda={w}:{h}:format={fmt}:interp_algo=nearest"
        ]
    },
    "vaapi": {
        "decode": [
            "-hwaccel", "vaapi",
        ],
        "encode": [
            "-preset", "fast"
        ]
        "scale": [
            "-vf", "hwupload,scale_vaapi=w={w}:h={h}",
        ]
    }
}

#process_video(filter_opts=vf_scale(), encode_opts=["-an", "-sn"])

def vf_scale(w=640, h=360, fmt='yuv444p', hwaccel="sw"):
    return [opt.format(w=w,h=h,fmt=fmt) for opt in scale_opts]

def ffmpeg_args(input_file, output_file, seek=None, to=None, hwaccel="sw", filter_opts=[], decode_opts=[], encode_opts=[]):
    args = ["ffmpeg"]
    args.extend(hwaccel_opts[hwaccel]['decode'])
    args.extend(decode_opts)
    hwaccel_opts[hwaccel] + ["-accurate_seek"]
    if seek is not None:
        args.extend(["-ss", f"{seek}"])
    if to is not None:
        args.extend(["-to", f"{to}"])
    args.extend(["-i", input_file])
    args.extend(filter_opts)
    args.extend(encode_opts)
    args.extend(hwaccel_opts[hwaccel]['encode'])
    args.append(output_file)
    return args

async def async_exec(args, stderr=None, stdout=None):
    proc = await asyncio.create_subprocess_exec(*args,stderr=stderr, stdout=stdout)
    return await proc.wait()

async def async_ffmpeg(input_file, output_file, seek=None, to=None, hwaccel="sw", filter_opts=[], decode_opts=[], encode_opts=[]):
    cmd = ffmpeg_args(input_file, output_file, seek, to, hwaccel=hwaccel, filter_opts, decode_opts, encode_opts)
    return await async_exec(cmd)