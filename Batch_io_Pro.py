# -*- coding:utf-8 -*-
# Author: 张来吃
# Version: 2.0.3
# Contact: laciechang@163.com

# 感谢 Igor Ridanovic 提供的时间码转换方法
# https://github.com/IgorRidanovic/smpte

# -----------------------------------------------------
# 本工具仅支持在达芬奇内运行
# -----------------------------------------------------

from PIL import ImageDraw, Image
import tempfile, math
# import DaVinciResolveScript as bmd

fu = bmd.scriptapp('Fusion')
ui = fu.UIManager
disp = bmd.UIDispatcher(ui)

clipcolor = {
    'Orange': [0, 110, 235],
    'Apricot': [51, 168, 255],
    'Yellow': [28, 169 ,226],
    'Lime': [21, 198, 159],
    'Olive': [32, 153, 94],
    'Green': [100, 143, 68],
    'Teal': [153, 152, 0],
    'Navy': [119, 50, 31],
    'Blue': [161, 118, 67],
    'Purple': [160, 115, 153],
    'Violet': [141, 87, 208],
    'Pink': [181, 140, 233],
    'Tan': [151, 176, 185],
    'Beige': [119, 160, 198],
    'Brown': [0, 102, 153],
    'Chocolate': [63, 90, 140]
}

PAR_MAPPING = {
    'Square': 1.0,
    '2.0': 2.0,
    '1.25': 1.25,
    '1.33': 1.33,
    '1.3x Anamorphic': 1.3,
    '1.5': 1.5,
    '1.8': 1.8,
    '16mm HD Anamorphic': 1.2857,
    '35mm Full Aperture HD Anamorphic': 1.35135,
    'NTSC': 1.111,
    'NTSC 16:9': 0.833,
    'NTSC DV': 1.125,
    'NTSC DV 16:9': 0.843,
    'PAL': 0.937,
    'PAL 16:9': 0.702,
    'Super16 HD Anamorphic': 1.0869
}

RESOLVE_FPS_MAPPING = {
    '16': 16.0,     '18': 18.0,
    '23': 23.976,   '24': 24.0,   '24.0': 24.0,
    '25': 25.0,     '29': 29.97,
    '30': 30.0,     '30.0': 30.0,     '47': 47.952,
    '48': 48.0,     '50': 50.0,
    '59': 59.94,    '60': 60.0,
    '72': 72.0,     '95': 95.904,
    '96': 96.0,     '100': 100.0,
    '119': 119.88,  '120': 120.0
}

class SMPTE(object):
	'''Frames to SMPTE timecode converter and reverse.'''
	def __init__(self):
		self.fps = 24
		self.df  = False


	def getframes(self, tc):
		'''Converts SMPTE timecode to frame count.'''

		if int(tc[9:]) > self.fps:
			raise ValueError ('SMPTE timecode to frame rate mismatch.', tc, self.fps)

		hours   = int(tc[:2])
		minutes = int(tc[3:5])
		seconds = int(tc[6:8])
		frames  = int(tc[9:])

		totalMinutes = int(60 * hours + minutes)

		# Drop frame calculation using the Duncan/Heidelberger method.
		if self.df:
			dropFrames = int(round(self.fps * 0.066666))
			timeBase   = int(round(self.fps))
			hourFrames   = int(timeBase * 60 * 60)
			minuteFrames = int(timeBase * 60)
			frm = int(((hourFrames * hours) + (minuteFrames * minutes) + (timeBase * seconds) + frames) - (dropFrames * (totalMinutes - (totalMinutes // 10))))
		# Non drop frame calculation.
		else:
			self.fps = int(round(self.fps))
			frm = int((totalMinutes * 60 + seconds) * self.fps + frames)

		return frm


	def gettc(self, frames):
		'''Converts frame count to SMPTE timecode.'''

		frames = abs(frames)

		# Drop frame calculation using the Duncan/Heidelberger method.
		if self.df:

			spacer = ':'
			spacer2 = ';'

			dropFrames         = int(round(self.fps * .066666))
			framesPerHour      = int(round(self.fps * 3600))
			framesPer24Hours   = framesPerHour * 24
			framesPer10Minutes = int(round(self.fps * 600))
			framesPerMinute    = int(round(self.fps) * 60 - dropFrames)

			frames = frames % framesPer24Hours

			d = frames // framesPer10Minutes
			m = frames % framesPer10Minutes

			if m > dropFrames:
				frames = frames + (dropFrames * 9 * d) + dropFrames * ((m - dropFrames) // framesPerMinute)
			else:
				frames = frames + dropFrames * 9 * d

			frRound = int(round(self.fps))
			hr = int(frames // frRound // 60 // 60)
			mn = int((frames // frRound // 60) % 60)
			sc = int((frames // frRound) % 60)
			fr = int(frames % frRound)

		# Non drop frame calculation.
		else:
			self.fps = int(round(self.fps))
			spacer  = ':'
			spacer2 = spacer

			frHour = self.fps * 3600
			frMin  = self.fps * 60

			hr = int(frames // frHour)
			mn = int((frames - hr * frHour) // frMin)
			sc = int((frames - hr * frHour - mn * frMin) // self.fps)
			fr = int(round(frames -  hr * frHour - mn * frMin - sc * self.fps))

		# Return SMPTE timecode string.
		return(
				str(hr).zfill(2) + spacer +
				str(mn).zfill(2) + spacer +
				str(sc).zfill(2) + spacer2 +
				str(fr).zfill(2)
				)

def icon_gen(bgr):
    rgb = tuple([bgr[2], bgr[1], bgr[0]])
    bg = Image.new('RGBA', (100, 100), (0,0,0,0))
    dot = ImageDraw.Draw(bg)
    dot.ellipse([1,1,99,99],fill = 'black', outline = None)
    dot.ellipse([10,10,90,90],fill = rgb, outline = None)
    tmp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    bg.save(tmp_file)
    return tmp_file.name

def getresolve(app='Resolve'):
    return bmd.scriptapp(app)

def this_pj():
    resolve = getresolve()
    pj_manager = resolve.GetProjectManager()
    current_pj = pj_manager.GetCurrentProject()
    return current_pj

def this_timeline():
    return this_pj().GetCurrentTimeline()

class Add_retime_render(object):
    def __init__(self, direction, key_color = 'Pink', render_preset = 'test_preset_name', track = 1, isVFXPullResoltion = False, ui_item=None):
        self.track_num = int(track)
        self.key_color = '' if key_color == '点击选取片段颜色' else key_color
        self.render_preset = render_preset
        self.isVFXPullResoltion = isVFXPullResoltion
        self.all_clips = this_timeline().GetItemsInTrack('video', self.track_num)
        self.direction = direction
        self.itm = ui_item
        self.pj = this_pj()

    def clips_reso_status(self, VFXPullReso):
        output = {}
        for i in self.all_clips:
            tClip = self.all_clips[i]
            clip_color = tClip.GetClipColor()
            mpi = tClip.GetMediaPoolItem()
            if clip_color == self.key_color:
                w, h = self.calc_output_height(tClip, VFXPullReso)
                reso = (w, h)
                clipinfo = {
                    'Name': tClip.GetName(),
                    'In': tClip.GetStart(),
                    'Resolution': mpi.GetClipProperty('Resolution') if mpi is not None else 'Null'
                }
                try:
                    output[reso].append(clipinfo)
                except:
                    output[reso] = [clipinfo]
        return output
    
    def calc_output_height(self, clip, width=2048):
        '''
        return width, height
        '''
        mpi = clip.GetMediaPoolItem()
        if mpi is not None:
            par = PAR_MAPPING[mpi.GetClipProperty('PAR')]
            res = str(mpi.GetClipProperty('Resolution')).split(sep='x')
            w, h = int(res[0]), int(res[1])

            if self.direction == "按宽度":
                if h > w or w <= width:
                    return w, h
                else:
                    height = math.floor(width / w * h / 2 / par) * 2
                    return int(width), int(height)

            if self.direction == "按高度":
                if h > w or h <= width:
                    return w, h
                else:
                    height = math.floor(width  / (h/par) * w / 2) * 2
                    return int(height), int(width)
        else:
            return 0, 0

    def total_job_count(self):
        total = 0
        for i in self.all_clips:
            tClip = self.all_clips[i]
            clip_color = tClip.GetClipColor()
            if clip_color == '':
                pass
            elif clip_color == self.key_color:
                total += 1
        return total
    
    def increase_pgbar(self, ratio):
        total_width = int(itm[ProgressBarBG].GetGeometry()[3])
        width = total_width * ratio
        self.itm[ProgressBar].Resize([int(width), 3])

    def render_single_clip(self, output_path ,VFXPullReso=2048):
        successed_job = 0
        total = self.total_job_count()
        self.itm[ProgressBar].Visible = True
        self.itm[ProgressBar].Resize([1, 3])
        self.itm[AddRenderJobs].Enabled = False
        for i in self.all_clips:
            tClip = self.all_clips[i]
            w, h = self.calc_output_height(tClip, VFXPullReso)
            clip_color = tClip.GetClipColor()
            if clip_color == '':
                print('Clip color is empty, passed.')
                pass
            elif clip_color == self.key_color:
                clip_in = tClip.GetStart()
                clip_out = tClip.GetEnd()
                render_settings = {
                    'MarkIn': int(clip_in),
                    'MarkOut': int(clip_out) - 1,
                    'TargetDir': output_path,
                }
                if self.isVFXPullResoltion is True:
                    render_settings['FormatWidth'] = w
                    render_settings['FormatHeight'] = h

                self.pj.LoadRenderPreset(self.render_preset)
                self.pj.SetRenderSettings(render_settings)
                jobId = self.pj.AddRenderJob()
                if len(jobId) >= 0:
                    successed_job += 1
                ratio = float(successed_job/total)
                self.increase_pgbar(ratio)
            else:
                pass
        self.itm[AddRenderJobs].Enabled = True

clipcolor_buttons = []
for i in list(clipcolor):
    color_bgr = clipcolor[i]
    temp_icon_path = icon_gen(color_bgr)
    clipcolor_buttons.append(ui.Button({'ID': i, 'Text': i, 'Flat': True, 'IconSize': [10, 10], 'Icon': ui.Icon({'File': temp_icon_path})}))

OutputPathPick = 'pickpath'
OutputPathStr = 'r_path'
ClipColorPicker = 'clipcolors'
RenderPresets = 'render_presets'
RefreshPresets = 'refresh_presets'
TrackNumber = 'tracknum'
RefreshTrack = 'refresh_track'
AddRenderJobs = 'add_job'
EnableVFXPullMode = 'EnableVFXPullMode'
DefaultWidth = 'default_width'
PreviewResolution = 'PreviewResolution'
DefaultDirection = 'DefaultDirection'
ProgressBar = 'progressbar'
ProgressBarBG = 'progressbarbg'

window_01 = [
        ui.HGroup({'Spacing': 10},
        [
            ui.VGroup({'Spacing': 10},[
                    ui.Label({'ID': 'label_01', 'Text': '将按指定预设 批量添加特定颜色片段 至渲染队列',}),
                    ui.HGap({'Spacing': 20}),
                    ui.Button({ 'ID': OutputPathPick, 'Text': '选择渲染输出路径', 'Default': True,}),
                    ui.LineEdit({'ID': OutputPathStr, 'PlaceholderText': '必选'}),
                    ui.HGap({'Spacing': 20}),
                    ui.Label({'ID': 'label_02', 'Text': '将按以下片段颜色添加渲染任务',}),
                    ui.Button({'ID': ClipColorPicker, 'Text': '点击选取片段颜色'}),
                    ui.Label({'ID': 'label_03', 'Text': '渲染所需渲染预设',}),
                    ui.HGroup({'Spacing': 10}, [
                        ui.ComboBox({'ID': RenderPresets, }),
                        ui.Button({'ID': RefreshPresets,'Text': '刷新', 'Weight': 0}),
                    ]),
                    ui.Label({'ID': 'label_04', 'Text': '将按以下视频轨道添加渲染任务',}),
                    ui.HGroup({'Spacing': 10}, [
                        ui.ComboBox({'ID': TrackNumber, 'Weight': 7}),
                        ui.Button({'ID': RefreshTrack,'Text': '刷新', 'Weight': 0}),
                    ]),
                    
                    ui.HGroup({"Spacing": 10}, [
                        ui.CheckBox({"ID": EnableVFXPullMode, "Text": "按VFX Pull常见规范自动计算输出分辨率"}),
                        ui.ComboBox({"ID": DefaultDirection, "Enabled": False}),
                        ui.DoubleSpinBox({"ID": DefaultWidth, "Decimals": 0, "Enabled": False, "Minimum": 1, "Maximum": 9999}),
                        ui.Button({"ID": PreviewResolution, "Text": "分辨率预览", 'Weight': 0}),
                    ]),
                    
                    ui.Button({'ID': AddRenderJobs, 'Text': 'Run', 'Weight': 7, 'Enabled': False}),
                    ui.HGap({'Spacing': 10}),
                    ui.Stack({"ID": "pg_set", "Visible": False,},[
                        ui.Label({"ID": ProgressBarBG,  "StyleSheet": "max-height: 3px; background-color: rgb(37,37,37)",}),
                        ui.Label({"ID": ProgressBar, "Visible":False, "StyleSheet": "max-height: 1px; background-color: rgb(102, 221, 39);border-width: 1px;border-style: solid;border-color: rgb(37,37,37);",})
                    ]),
            ]),
        ]),
    ]

dlg = disp.AddWindow({ 
                        'WindowTitle': 'Batch Render Tools Pro', 
                        'ID': 'MyWin',
                        'Geometry': [ 
                                    800, 500, # position when starting
                                    600, 400 # width, height
                         ], 
                        },
    window_01)
 
itm = dlg.GetItems()
itm[DefaultWidth].Value = 2048
itm[DefaultDirection].AddItems(["按宽度", "按高度"])


def _exit(ev):
    disp.ExitLoop()
dlg.On.MyWin.Close = _exit

# ----------------------------------------------
def load_preset():
    itm[RenderPresets].Clear()
    preset_list = this_pj().GetRenderPresets()
    for i in list(preset_list.keys()):
        preset = preset_list[i]
        itm[RenderPresets].AddItem(str(preset))

def load_track_count():
    itm[TrackNumber].Clear()
    v_track = int(this_timeline().GetTrackCount('video'))
    for i in range(1, v_track + 1):
        itm[TrackNumber].AddItem(str(i))

def _isVFXResolution(ev):
    itm[DefaultWidth].Enabled = bool(1-itm[DefaultWidth].GetEnabled())
    itm[DefaultDirection].Enabled = bool(1-itm[DefaultDirection].GetEnabled())

def _pop_resolution_status_window(ev):
    # 获得分辨率列表
    color = itm[ClipColorPicker].Text
    track = int(itm[TrackNumber].CurrentText)
    add = Add_retime_render(direction = itm[DefaultDirection].CurrentText ,key_color = color, track = track)
    resolution_list = add.clips_reso_status(itm[DefaultWidth].Value) 

    # 创建 基本window
    popup_status_window = [ui.HGroup({"Spacing": 5}, [
        ui.Tree({"ID": "reso_tree", 'Weight': 0.3}),
        ui.Tree({"ID": "reso_clip_tree", 'Weight': 0.7})
    ])]
    win_height = len(resolution_list)*30+120
    bt_pos = itm[PreviewResolution].GetGeometry()
    main_pos = dlg.GetGeometry()
    reso_win = disp.AddWindow({ 
                        "WindowTitle": "Clip Res List", 
                        "ID": "reso_prev",  
                        # "WindowFlags": {"SplashScreen" : True},
                        "Geometry": [ 
                                    main_pos[1] + bt_pos[3]+ 400, main_pos[2] + bt_pos[2] + 100, # position when starting
                                    550, win_height # width, height
                         ], 
                        "WindowFlags":{
                            "Window": True,
                        }
                        },
                        popup_status_window)
    
    def __exit(ev):
        disp.ExitLoop()
    
    reso_item = reso_win.GetItems()
    reso_tree = reso_item['reso_tree']
    clip_tree = reso_item['reso_clip_tree']
    reso_head = reso_tree.NewItem()
    cliptree_head = clip_tree.NewItem()

    reso_head.Text[0] = 'Width'
    reso_head.Text[1] = 'Height'
    reso_tree.SetHeaderItem(reso_head)
    cliptree_head.Text[0] = 'Clip Name'
    cliptree_head.Text[1] = 'In Point'
    cliptree_head.Text[2] = 'Original Resolution'
    clip_tree.SetHeaderItem(cliptree_head)

    reso_tree.ColumnWidth[0] = 70
    reso_tree.ColumnWidth[1] = 70
    clip_tree.ColumnWidth[0] = 150
    clip_tree.ColumnWidth[1] = 90
    clip_tree.ColumnWidth[2] = 70

    rows = []
    for res in resolution_list:
        row = reso_tree.NewItem()
        row.Text[0] = str(res[0])
        row.Text[1] = str(res[1])
        rows.append(row)
    reso_tree.AddTopLevelItems(rows)

    TIMELINE_FPS = str(this_timeline().GetSetting('timelineFrameRate'))
    
    def _select_reso_tree(ev):
        smpte = SMPTE()
        smpte.fps = RESOLVE_FPS_MAPPING[TIMELINE_FPS]
        smpte.df = bool(int(this_timeline().GetSetting('timelineDropFrameTimecode')))

        clip_tree = reso_item['reso_clip_tree']
        clip_tree.Clear()
        selected = reso_item['reso_tree'].CurrentItem()
        key = (int(selected.Text[0]), int(selected.Text[1]))
        result = resolution_list[key]
        cliprows = []
        for clipgp in result:
            cliprow = clip_tree.NewItem()
            cliprow.Text[0] = str(clipgp['Name'])
            cliprow.Text[1] = str(smpte.gettc(clipgp['In']))
            cliprow.Text[2] = str(clipgp['Resolution'])
            cliprows.append(cliprow)
        clip_tree.AddTopLevelItems(cliprows)
    
    def _jump_to_target_clip(ev):
        timecode = reso_item['reso_clip_tree'].CurrentItem().Text[1]
        this_timeline().SetCurrentTimecode(timecode)

    reso_win.On['reso_tree'].ItemClicked = _select_reso_tree
    reso_win.On['reso_clip_tree'].ItemClicked = _jump_to_target_clip
    reso_win.On['reso_prev'].Close = __exit

    reso_win.Show()
    disp.RunLoop()
    reso_win.Hide()


def _release_run_button(ev):
    if len(itm[OutputPathStr].Text) >= 1:
        itm[AddRenderJobs].Enabled = True
        itm['pg_set'].Visible = True
    else:
        itm[AddRenderJobs].Enabled = False
        itm['pg_set'].Visible = False

def _pickfile(ev):
    selected = fu.RequestDir()
    itm[OutputPathStr].Text = str(selected)
    return selected

def _run_add(ev):
    enabled = itm[EnableVFXPullMode].Checked
    path = itm[OutputPathStr].GetText()
    preset = itm[RenderPresets].CurrentText
    color = itm[ClipColorPicker].Text
    track = int(itm[TrackNumber].CurrentText)
    add = Add_retime_render(ui_item=itm ,direction = itm[DefaultDirection].CurrentText ,render_preset = preset, key_color = color, track = track, isVFXPullResoltion=enabled)
    add.render_single_clip(path, VFXPullReso = int(itm[DefaultWidth].Value))



def _refresh_presets(ev):
    load_preset()

def _refresh_track(ev):
    load_track_count()

def _clipcolor_popup(ev):
    bt_pos = itm[ClipColorPicker].GetGeometry()
    main_pos = dlg.GetGeometry()
    new_win = disp.AddWindow({ 
                        'WindowTitle': 'Clip Color List', 
                        'ID': 'colorlist',  
                        'WindowFlags': {'Popup' : True},
                        'Geometry': [ 
                                    main_pos[1] + bt_pos[3]+ 20, main_pos[2] + bt_pos[2] , # position when starting
                                    120, 500 # width, height
                         ], 
                        },
                        [ui.VGroup(clipcolor_buttons)])
    
    def __change_combo(ev):
        who_clicked = ev['who']
        itm[ClipColorPicker].Text = who_clicked
        disp.ExitLoop()

    for i in list(clipcolor):
        new_win.On[i].Clicked = __change_combo

    new_win.Show()
    disp.RunLoop()
    new_win.Hide()

load_preset()
load_track_count()

dlg.On[OutputPathPick].Clicked = _pickfile
dlg.On[AddRenderJobs].Clicked = _run_add
dlg.On[RefreshPresets].Clicked = _refresh_presets
dlg.On[RefreshTrack].Clicked = _refresh_track
dlg.On[ClipColorPicker].Clicked = _clipcolor_popup
dlg.On[OutputPathStr].TextChanged = _release_run_button
dlg.On[EnableVFXPullMode].Clicked = _isVFXResolution
dlg.On[PreviewResolution].Clicked = _pop_resolution_status_window


if __name__ == "__main__":
    dlg.Show()
    disp.RunLoop()
    dlg.Hide()