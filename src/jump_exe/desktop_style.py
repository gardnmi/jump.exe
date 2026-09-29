"""Omarchy Osaka Jade colors, sampled from its published theme, frozen for the game.

https://github.com/basecamp/omarchy/blob/master/themes/osaka-jade/colors.toml
No user's theme/configuration is read or changed at runtime.
"""


def rgb(value):
    return tuple(int(value[i:i+2],16)/255 for i in (1,3,5))


BG=rgb('#111c18')
DEEP=rgb('#090f0d')
PANEL=rgb('#23372B')
MUTED=rgb('#53685B')
TEXT=rgb('#C1C497')
WHITE=rgb('#F6F5DD')
JADE=rgb('#509475')
GREEN=rgb('#63b07a')
CYAN=rgb('#2DD5B7')
RED=rgb('#FF5345')
YELLOW=rgb('#E5C736')
PINK=rgb('#D2689C')
BLUE=rgb('#ACD4CF')
FONT='CaskaydiaMono Nerd Font'
ACCENTS=(JADE,RED,YELLOW,BLUE,CYAN)


def mix(a,b,amount):
    return tuple(x*(1-amount)+y*amount for x,y in zip(a,b))


# The same Omarchy accent family, with different light/material environments.
# These are pane-local colors; the actual desktop wallpaper is never painted.
SCENES = (
    dict(back=rgb('#202720'), panel=rgb('#344236'), metal=rgb('#858975'), ink=TEXT),
    dict(back=rgb('#291916'), panel=rgb('#482721'), metal=rgb('#97644B'), ink=rgb('#F0B48C')),
    dict(back=rgb('#282719'), panel=rgb('#45432D'), metal=rgb('#9B9470'), ink=rgb('#D5CD9D')),
    dict(back=rgb('#0C121B'), panel=rgb('#1A2731'), metal=rgb('#435B68'), ink=rgb('#8EACB7')),
    dict(back=rgb('#163437'), panel=rgb('#285554'), metal=rgb('#82B3A0'), ink=rgb('#D1E8CB')),
)


APPS=('nvim','settings','terminal','build','btop','lazygit','permissions',
      'nvim','diff','terminal','help','nvim','tmux','checks','terminal')
PATHS=('~/code/main.py','~/.config/ai','~/code/autocomplete','~/code/build.log',
       '~/code/fix-final-v9','~/code/.git','~/code/AGENTS.md','~/code/app.test',
       '~/code/review','~/code/idle','~/code/forgotten','~/code/untitled',
       '~/code/together','~/code/checks','~/code/what-next')
