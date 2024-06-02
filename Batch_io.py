# -*- coding:utf-8 -*-
# Author: 张来吃
# Version: 1.1
# Contact: laciechang@163.com

# -----------------------------------------------------
# This script must be run in DaVinci Resolve only.
# -----------------------------------------------------

def getresolve(app='Resolve'):
    return bmd.scriptapp(app)

def get_fusion():
    return getresolve('Fusion')

def this_pj():
    resolve = getresolve()
    pj_manager = resolve.GetProjectManager()
    current_pj = pj_manager.GetCurrentProject()
    return current_pj

def this_timeline():
    timeline = this_pj().GetCurrentTimeline()
    return timeline

class Add_retime_render():

    def __init__(self, output_path, file_name = 'Utitled', key_color = 'Pink', render_preset = 'test_preset_name', track = 1):
        self.track_num = int(track)
        self.output_path = output_path
        self.file_name = file_name
        self.key_color = key_color
        self.render_preset = render_preset
        self.all_clips = this_timeline().GetItemsInTrack('video', self.track_num)

    def render_single_clip(self):
        #all_clips = self.all_clips
        pj = this_pj()
        for i in self.all_clips:
            clip_color = self.all_clips[i].GetClipColor()
            if clip_color == '':
                print('No need to render this clip')
                pass
            else:
                if clip_color in self.key_color:
                    clip_in = self.all_clips[i].GetStart()
                    clip_out = self.all_clips[i].GetEnd()
                    render_settings = {
                        'MarkIn': int(clip_in),
                        'MarkOut': int(clip_out) - 1,
                        'TargetDir': self.output_path,
                        #'CustomName': self.file_name
                    }
                    pj.LoadRenderPreset(self.render_preset)
                    pj.SetRenderSettings(render_settings)
                    pj.AddRenderJob()
                else:
                    print('No clip to render')
                    pass

clip_colors = ['Orange', 'Apricot', 'Yellow', 'Lime', 'Olive', 'Green', 'Teal', 'Navy', 'Blue', 'Purple', 'Violet', 'Pink', 'Tan', 'Beige', 'Brown', 'Chocolate']

fu = get_fusion() 
ui = fu.UIManager
disp = bmd.UIDispatcher(ui)

window_01 = [
        ui.HGroup({"Spacing": 10},
        [
            ui.VGroup({"Spacing": 10},[
                    ui.Label({"ID": 'label_01', "Text": "将按指定预设 批量添加特定颜色片段 至渲染队列",}),
                    ui.HGap({"Spacing": 20}),
                    ui.Button({ "ID": "pickpath", "Text": "选择渲染输出路径", "Default": True,}),
                    ui.LineEdit({"ID": "r_path", "PlaceholderText": "必选"}),
                    ui.HGap({"Spacing": 20}),
                    ui.Label({"ID": 'label_02', "Text": "将按以下片段颜色添加渲染任务",}),
                    ui.ComboBox({"ID": "clipcolors",}),
                    ui.Label({"ID": 'label_03', "Text": "渲染所需渲染预设",}),
                    ui.HGroup({"Spacing": 10}, [
                        ui.ComboBox({"ID": "render_presets", "Weight": 7}),
                        ui.Button({"ID": "refresh_presets","Text": "刷新"}),
                    ]),
                    ui.Label({"ID": 'label_04', "Text": "将按以下视频轨道添加渲染任务",}),
                    ui.HGroup({"Spacing": 10}, [
                        ui.ComboBox({"ID": "tracknum", "Weight": 7}),
                        ui.Button({"ID": "refresh_track","Text": "刷新"}),
                    ]),
                    
                    ui.HGap({"Spacing": 10}),
                    ui.Button({"ID": "add_job", "Text": "Run", "Enabled": False, "Weight": 7}),
                    ui.HGap({"Spacing": 10}),
            ]),
        ]),
    ]

current_window = window_01

dlg = disp.AddWindow({ 
                        "WindowTitle": "Batch Render Tools v1.1", 
                        "ID": "MyWin", 
                        "Geometry": [ 
                                    600, 300, # position when starting
                                    400, 400 # width, height
                         ], 
                        "WindowFlags": {
                            "Window": True,
                            "WindowStaysOnTopHint": True,
                        },
                        },
    current_window)
 
itm = dlg.GetItems()
 
def _func(ev):
    disp.ExitLoop()
dlg.On.MyWin.Close = _func

# ----------------------------------------------

def load_preset():
    itm['render_presets'].Clear()
    preset_list = this_pj().GetRenderPresets()
    for i in list(preset_list.keys()):
        preset = preset_list[i]
        itm['render_presets'].AddItem(str(preset))

def load_track_count():
    itm['tracknum'].Clear()
    v_track = int(this_timeline().GetTrackCount('video'))
    for i in range(1, v_track + 1):
        itm['tracknum'].AddItem(str(i))


def _pickfile(ev):
    selected = fu.RequestDir()
    itm['r_path'].Text = str(selected)
    return selected

def _run_add(ev):
    path = itm['r_path'].GetText()
    preset = itm['render_presets'].CurrentText
    color = itm['clipcolors'].CurrentText
    track = int(itm['tracknum'].CurrentText)
    add = Add_retime_render(path, render_preset = preset, key_color = color, track = track)
    add.render_single_clip()

def _refresh_presets(ev):
    load_preset()

def _refresh_track(ev):
    load_track_count()

def _release_run_button(ev):
    if len(itm['r_path'].Text) >= 1:
        itm['add_job'].Enabled = True
    else:
        itm['add_job'].Enabled = False

for colr in clip_colors:
    itm['clipcolors'].AddItem(colr)

load_preset()
load_track_count()

dlg.On.pickpath.Clicked = _pickfile
dlg.On.add_job.Clicked = _run_add
dlg.On.refresh_presets.Clicked = _refresh_presets
dlg.On.refresh_track.Clicked = _refresh_track
dlg.On.r_path.TextChanged = _release_run_button

if __name__ == "__main__":
    dlg.Show()
    disp.RunLoop()
    dlg.Hide()