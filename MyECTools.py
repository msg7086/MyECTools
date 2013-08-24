class MyECTools():
    def __init__(self, core, use_internal_overlay = False):
        self.core = core
        self.avs = core.avs
        self.std = core.std
        if self.core.list_functions().find('Overlay') == -1 or use_internal_overlay:
            self.Overlay = self.ECOverlay
            print('Using internal overlay')
        else:
            self.Overlay = self.avs.Overlay
            print('Using avisynth overlay')

    def ECSlice(self, clip, l = 0, t = 0, r = 0, b = 0, sp1 = None, sp2 = None, spmode = 0):
        if sp1 is not None and not callable(sp1):
            raise ValueError('ECSlice: sp1 is not callable')
        if sp2 is not None and not callable(sp2):
            raise ValueError('ECSlice: sp2 is not callable')

        img_sliced = self._sp1_func(clip, l, t, r, b, sp1, spmode)

        if l == 0 and t == 0 and r == 0 and b == 0:
            return img_sliced

        img_outline = self._sp2_func(clip, sp2)

        img_overlay = self.Overlay(img_outline, img_sliced, l, t)

        return img_overlay


    def _sp1_func(self, clip, l = 0, t = 0, r = 0, b = 0, sp1 = None, spmode = 0):
        if sp1 is None:
            return self._eccrop(clip, l, t, r, b)

        newclip = clip

        if spmode == 0:
            newclip = sp1(newclip)

        newclip = self._eccrop(newclip, l, t, r, b)
        if spmode != 0:
            newclip = sp1(newclip)

        return newclip;

    def _sp2_func(self, clip, sp2 = None):
        if sp2 is None:
            return clip
        return sp2(clip)

    def _eccrop(self, clip, l = 0, t = 0, r = 0, b = 0):
        if l == 0 and t == 0 and r == 0 and b == 0:
            return clip
        return self.std.CropRel(clip, left = l, top = t, right = r, bottom = b)

    def ECOverlay(self, clip_outline, clip_sliced, l = 0, t = 0):
        clip_left = clip_right = clip_top = clip_bottom = None
        r = clip_outline.width - clip_sliced.width - l
        b = clip_outline.height - clip_sliced.height - t

        # Slicing
        if l > 0:
            clip_left = self.std.CropAbs(clip_outline, x = 0, y = 0, width = l, height = clip_outline.height)
        if r > 0:
            clip_right = self.std.CropAbs(clip_outline, x = clip_outline.width-r, y = 0, width = r, height = clip_outline.height)
        if t > 0:
            clip_top = self.std.CropAbs(clip_outline, x = l, y = 0, width = clip_outline.width-l-r, height = t)
        if b > 0:
            clip_bottom = self.std.CropAbs(clip_outline, x = l, y = clip_outline.height-b, width = clip_outline.width-l-r, height = b)

        # Merging
        Verticals = [clip for clip in [clip_top, clip_sliced, clip_bottom] if clip is not None]

        if len(Verticals) == 1:
            clip_middle = Verticals[0]
        else:
            clip_middle = self.std.StackVertical(Verticals)

        Horizontals = [clip for clip in [clip_left, clip_middle, clip_right] if clip is not None]

        if len(Horizontals) == 1:
            newclip = Horizontals[0]
        else:
            newclip = self.std.StackHorizontal(Horizontals)

        return newclip
