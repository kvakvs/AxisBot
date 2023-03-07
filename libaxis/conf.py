import yaml

conf = yaml.load(open('config.yaml', encoding='utf-8-sig').read(), Loader=yaml.Loader)
bot_conf = conf['bot']
guild_conf = conf['guild']
