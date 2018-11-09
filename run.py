import os
import json
import matplotlib.pyplot as plt
from attrdict import AttrDict
from PIL import Image, ImageFont, ImageDraw

plt.ion()


def get_all_people(path):
    res = []
    for root, dirs, files in os.walk(path):
        for i in files:
            if i == '.DS_Stor':
                continue
            res.append(os.path.join(root, i))
    return res


def parser_file_name(file_path: str):
    path, name = os.path.split(file_path)
    res = (name.split('.')[0]).split('_')
    return {
        'name': res[2],
        'pos': res[0],
        'rank': res[1],
    }


people_path = './people'
output_path = './output'

if not os.path.exists(output_path):
    os.mkdir(output_path)

def run():
    gzz_list = get_all_people('./gzz')
    base_map = {}

    font_config = {}

    with open('./font_config.json', 'r') as f:
        font_config = json.load(f)

    for file in gzz_list:
        base = Image.open(file)
        plt.imshow(base, cmap=plt.get_cmap("gray"))
        print("get photo pos")
        pos = plt.ginput(5)
        (photo_l, photo_r, name_pos, pos_pos, rank_pos) = ((int(p[0]), int(p[1])) for p in pos)
        photo_width = photo_r[0] - photo_l[0]
        photo_height = photo_r[1] - photo_l[1]
        print("photo pos: {}".format((photo_l, photo_r, photo_width, photo_height)))
        print("name pos{}".format(name_pos))
        print("pos pos{}".format(pos_pos))
        print("rank pos{}".format(rank_pos))
        base_info = AttrDict({
            'photo_l': photo_l,
            'photo_r': photo_r,
            'photo_width': photo_width,
            'photo_height': photo_height,
            'pos_pos': pos_pos,
            'name_pos': name_pos,
            'rank_pos': rank_pos
        })
        base_map[os.path.split(file)[-1].split('.')[0]] = (base.copy(), base_info)

    persons = get_all_people(people_path)
    err_list = []
    for p in persons:
        try:
            info = parser_file_name(p)
        except Exception:
            print("错误的图片名字格式, {}".format(p))
            err_list.append(p)
            continue
        print("处理 {}".format(info))
        try:
            base, base_info = base_map[info['rank']]
        except Exception:
            print("没有该职位对应的工作证 {}, {}".format(info['rank'], info))
            err_list.append(p)
            continue

        base_c = base.copy()
        try:
            photo = Image.open(p)
        except Exception:
            print("证件照格式异常 {}, {}".format(p,info))
            err_list.append(p)
            continue
        photo = photo.resize((int(base_info.photo_width), int(base_info.photo_height)))
        print("处理照片完成")
        base_c.paste(photo, base_info.photo_l)
        base_c_dr = ImageDraw.Draw(base_c)

        name_font = ImageFont.truetype('wq.ttf', font_config['name']['size'])
        base_c_dr.text(base_info.name_pos, info['name'], font=name_font, fill=font_config['name']['color'])

        pos_font = ImageFont.truetype('wq.ttf', font_config['pos']['size'])
        base_c_dr.text(base_info.pos_pos, info['pos'], font=pos_font, fill=font_config['pos']['color'])

        rank_font = ImageFont.truetype('wq.ttf', font_config['rank']['size'])
        base_c_dr.text(base_info.rank_pos, info['rank'], font=rank_font, fill=font_config['rank']['color'])
        print("处理字体")

        if not os.path.exists(os.path.join(output_path, info["rank"])):
            os.mkdir(os.path.join(output_path, info["rank"]))
        base_c.save(os.path.join(os.path.join(output_path, info["rank"]), '{name}_{pos}_{rank}.png'.format(**info)), dpi=(300.0,300.0))


if __name__ == '__main__':
    run()
