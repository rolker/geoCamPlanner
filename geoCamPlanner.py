#!/usr/bin/env python3

import geoCamPlannerUI
import wx
import wxmpl
import math
import xml.etree.ElementTree
import sys
import matplotlib
import matplotlib.pyplot

class Configuration:
    defaults = (('fx',1280.0),
                ('fy',1280.0),
                ('ix',2560),
                ('iy',1920),
                ('ixmm',5.76),
                ('iymm',4.29),
                ('max_zoom',1.0),
                ('range',1000.0),
                ('height',30.0),
                ('pan_angle',90.0),
                ('tilt_angle',-5.0),
                ('resolution',1.0),
                ('roll_range',1.5)
               )
    ints = ('ix','iy')
                                        
    def __init__(self, copyFrom = None):
        self.values = {}
        self.description = ''
        if copyFrom is None:
            for d in Configuration.defaults:
                self.values[d[0]]=d[1]
        else:
            self.description = copyFrom.description
            for d in Configuration.defaults:
                self.values[d[0]] = copyFrom.values[d[0]]

    def saveTo(self,outfile,label):
        outfile.write('    <Configuration')
        outfile.write(' label="'+label+'"')
        for v in Configuration.defaults:
            outfile.write(' '+v[0]+'="'+str(self.values[v[0]])+'"')
        outfile.write('>'+self.description+'</Configuration>\n')

    def loadFrom(self, node):
        for v in Configuration.defaults:
            try:
                if v[0] in Configuration.ints:
                    self.values[v[0]] = int(node.attrib[v[0]])
                else:
                    self.values[v[0]] = float(node.attrib[v[0]])
            except KeyError:
                self.values[v[0]] = v[1]
                    
        if node.text is not None:
            self.description = node.text
        else:
            self.description = ''

class GeoCamPlanner(geoCamPlannerUI.geoCamPlannerBase):
    def __init__(self,fname=None):
        
        geoCamPlannerUI.geoCamPlannerBase.__init__(self,None, -1, "")
        self.updating = False

        self.plots = wxmpl.PlotPanel(self,-1)
        self.footprint_axes = self.plots.get_figure().add_axes((0.1,0.5,0.8,0.3))
        self.geometry_axes = self.plots.get_figure().add_axes((0.1,0.1,0.8,0.3),sharex=self.footprint_axes)
        
        self.GetSizer().Add(self.plots,1,wx.EXPAND)

        #self.geometryPlot = wxmpl.PlotPanel(self,-1)
        #self.GetSizer().Add(self.geometryPlot,1,wx.EXPAND)


        self.GetSizer().Fit(self)
        self.Layout()

        self.clear()
        if fname is not None:
            self.open(fname)

    def clear(self):
        self.filename = None
        self.configComboBox.Clear()
        self.setCurrentConfig(None)

    def open(self, fname):
        tree = xml.etree.ElementTree.parse(fname)
        root = tree.getroot()
        configs = root.findall('Configuration')
        for c in configs:
            config = Configuration()
            config.loadFrom(c)
            self.configComboBox.Append(c.attrib['label'],config)
        self.filename = fname

    def save(self, fname):
        if fname is None:
            fname = self.filename
        if fname is not None:
            outfile = open(fname,'w')
            outfile.write('<geoCamera>\n')
            for i in range(self.configComboBox.GetCount()):
                self.configComboBox.GetClientData(i).saveTo(outfile,self.configComboBox.GetString(i))
            outfile.write('</geoCamera>\n')
            self.filename = fname

    def setCurrentConfig(self, c):
        self.currentConfig = c
        self.updateGUI()
        self.enableGUI(c is not None)


    def enableGUI(self,e=True):
        self.baseFXTextCtrl.Enable(e)
        self.baseFYTextCtrl.Enable(e)
        self.baseFXMMTextCtrl.Enable(e)
        self.baseFYMMTextCtrl.Enable(e)
        self.imagerSizeXTextCtrl.Enable(e)
        self.imagerSizeYTextCtrl.Enable(e)
        self.imagerSizeXMMTextCtrl.Enable(e)
        self.imagerSizeYMMTextCtrl.Enable(e)
        self.maxZoomTextCtrl.Enable(e)
        self.rangeTextCtrl.Enable(e)
        self.heightTextCtrl.Enable(e)
        self.panAngleTextCtrl.Enable(e)
        self.tiltAngleTextCtrl.Enable(e)
        if self.fixedBaseFOVCheckBox.GetValue():
            self.baseFovXTextCtrl.Enable(False)
            self.baseFovYTextCtrl.Enable(False)
        else:
            self.baseFovXTextCtrl.Enable(e)
            self.baseFovYTextCtrl.Enable(e)
        self.maxFXTextCtrl.Enable(e)
        self.maxFYTextCtrl.Enable(e)
        self.maxFXMMTextCtrl.Enable(e)
        self.maxFYMMTextCtrl.Enable(e)
        self.maxFovXTextCtrl.Enable(e)
        self.maxFovYTextCtrl.Enable(e)
        self.resolutionTextCtrl.Enable(e)
        self.rollRangeTextCtrl.Enable(e)
        self.configDescriptionTextCtrl.Enable(e)
        self.saveGraphButton.Enable(e)
        self.fixedPixelAspectCheckBox.Enable(e)
        self.fixedBaseFOVCheckBox.Enable(e)

    def updateGUI(self):
        self.updating = True

        if self.currentConfig is not None:
            self.baseFXTextCtrl.SetValue(str(self.currentConfig.values['fx']))
            self.baseFYTextCtrl.SetValue(str(self.currentConfig.values['fy']))
            self.imagerSizeXTextCtrl.SetValue(str(self.currentConfig.values['ix']))
            self.imagerSizeYTextCtrl.SetValue(str(self.currentConfig.values['iy']))
            self.imagerSizeXMMTextCtrl.SetValue(str(self.currentConfig.values['ixmm']))
            self.imagerSizeYMMTextCtrl.SetValue(str(self.currentConfig.values['iymm']))
            self.baseFXMMTextCtrl.SetValue(str(self.currentConfig.values['fx']*self.currentConfig.values['ixmm']/float(self.currentConfig.values['ix'])))
            self.baseFYMMTextCtrl.SetValue(str(self.currentConfig.values['fy']*self.currentConfig.values['iymm']/float(self.currentConfig.values['iy'])))
            self.maxZoomTextCtrl.SetValue(str(self.currentConfig.values['max_zoom']))
            self.rangeTextCtrl.SetValue(str(self.currentConfig.values['range']))
            self.heightTextCtrl.SetValue(str(self.currentConfig.values['height']))
            self.panAngleTextCtrl.SetValue(str(self.currentConfig.values['pan_angle']))
            self.tiltAngleTextCtrl.SetValue(str(self.currentConfig.values['tilt_angle']))
            self.baseFovXTextCtrl.SetValue(str(math.degrees(2.0*math.atan2(self.currentConfig.values['ix']/2.0,self.currentConfig.values['fx']))))
            self.baseFovYTextCtrl.SetValue(str(math.degrees(2.0*math.atan2(self.currentConfig.values['iy']/2.0,self.currentConfig.values['fy']))))
            self.maxFXTextCtrl.SetValue(str(self.currentConfig.values['fx']*self.currentConfig.values['max_zoom']))
            self.maxFYTextCtrl.SetValue(str(self.currentConfig.values['fy']*self.currentConfig.values['max_zoom']))
            self.maxFXMMTextCtrl.SetValue(str(self.currentConfig.values['fx']*self.currentConfig.values['max_zoom']*self.currentConfig.values['ixmm']/float(self.currentConfig.values['ix'])))
            self.maxFYMMTextCtrl.SetValue(str(self.currentConfig.values['fy']*self.currentConfig.values['max_zoom']*self.currentConfig.values['iymm']/float(self.currentConfig.values['iy'])))
            self.maxFovXTextCtrl.SetValue(str(math.degrees(2.0*math.atan2(self.currentConfig.values['ix']/2.0,self.currentConfig.values['fx']*self.currentConfig.values['max_zoom']))))
            self.maxFovYTextCtrl.SetValue(str(math.degrees(2.0*math.atan2(self.currentConfig.values['iy']/2.0,self.currentConfig.values['fy']*self.currentConfig.values['max_zoom']))))
            self.resolutionTextCtrl.SetValue(str(self.currentConfig.values['resolution']))
            self.rollRangeTextCtrl.SetValue(str(self.currentConfig.values['roll_range']))
            self.configDescriptionTextCtrl.SetValue(self.currentConfig.description)
        else:
            self.enableGUI(False)
            self.baseFXTextCtrl.Clear()
            self.baseFYTextCtrl.Clear()
            self.baseFXMMTextCtrl.Clear()
            self.baseFYMMTextCtrl.Clear()
            self.imagerSizeXTextCtrl.Clear()
            self.imagerSizeYTextCtrl.Clear()
            self.imagerSizeXMMTextCtrl.Clear()
            self.imagerSizeYMMTextCtrl.Clear()
            self.maxZoomTextCtrl.Clear()
            self.rangeTextCtrl.Clear()
            self.heightTextCtrl.Clear()
            self.panAngleTextCtrl.Clear()
            self.tiltAngleTextCtrl.Clear()
            self.baseFovXTextCtrl.Clear()
            self.baseFovYTextCtrl.Clear()
            self.maxFXTextCtrl.Clear()
            self.maxFYTextCtrl.Clear()
            self.maxFXMMTextCtrl.Clear()
            self.maxFYMMTextCtrl.Clear()
            self.maxFovXTextCtrl.Clear()
            self.maxFovYTextCtrl.Clear()
            self.resolutionTextCtrl.Clear()
            self.rollRangeTextCtrl.Clear()
            self.configDescriptionTextCtrl.Clear()

        self.updating = False

        self.updatePlots()

    def updatePlots(self):

        fig = self.plots.get_figure()
        fig.clear()

        bright_green = (0.0,1.0,0.0,1.0)
        bright_red = (1.0,0.0,0.0,1.0)
        pale_green = (0.5,1.0,0.5,1.0)
        pale_red = (1.0,0.5,0.5,1.0)

        footprint_axes = self.plots.get_figure().add_axes((0.25,0.675,0.7,0.25))
        geometry_axes = self.plots.get_figure().add_axes((0.025,0.025,0.45,0.575))
        top_axes = self.plots.get_figure().add_axes((0.5,0.025,0.45,0.575))

        if self.currentConfig is not None:
            fig.text(.05,.75,self.currentConfig.description)

            zooms = [1.0]

            
            
            if self.currentConfig.values['max_zoom'] > 1.0:
                zooms.append(self.currentConfig.values['max_zoom'])

            legend_axes = [matplotlib.pyplot.Rectangle((0,0),1,1,fc=pale_green), matplotlib.pyplot.Rectangle((0,0),1,1,fc=pale_red)]
            footprint_legend_labels = []
            geomtry_legend_labels = []
            if len(zooms) == 1:
                footprint_legend_labels.append('footprint < resolution')
                footprint_legend_labels.append('footprint > resolution')
                geomtry_legend_labels.append('always visible')
                geomtry_legend_labels.append('sometimes visible')
            else:
                footprint_legend_labels.append('footprint < resolution (min zoom)')
                footprint_legend_labels.append('footprint > resolution (min zoom)')
                geomtry_legend_labels.append('always visible (min zoom)')
                geomtry_legend_labels.append('sometimes visible (min zoom)')
                
            max_y = None
            for z in zooms:
                
                hfovx = math.atan2(self.currentConfig.values['ix']/2.0,self.currentConfig.values['fx']*z)
                pan_factor = math.radians(abs(90.0 - self.currentConfig.values['pan_angle']))
                if(pan_factor < hfovx):
                    pan_factor = 0.0
                else:
                    pan_factor = pan_factor - hfovx
                pan_factor = math.cos(pan_factor)
                
                #hpfovy = math.atan2(.5,self.currentConfig.values['fy']*z) # half the fov of a pixel

                sensor_angles = []
                ref = self.currentConfig.values['iy']/2.0
                for i in range(self.currentConfig.values['iy']+1):
                    sensor_angles.append(math.atan2(i-ref,self.currentConfig.values['fy']*z))

                sensor_angles_x = []
                ref = self.currentConfig.values['ix']/2.0
                N = 100
                for i in range(N):  # range(self.currentConfig.values['ix']+1):
                    i *= self.currentConfig.values['ix']/float(N)
                    sensor_angles_x.append(math.atan2(i-ref,self.currentConfig.values['fx']*z))

                rr = math.radians(self.currentConfig.values['roll_range'])
                #start_angle =  math.radians(self.currentConfig.values['tilt_angle'])-hpfovy*(self.currentConfig.values['iy']-1)
                #end_angle = start_angle + 2*hpfovy*self.currentConfig.values['iy']
                start_angle =  math.radians(self.currentConfig.values['tilt_angle'])+sensor_angles[0] 
                end_angle = start_angle + (sensor_angles[-1]-sensor_angles[0])

                x = []
                y = []
                ok = []
                notOk = []

                top_x_ok = []
                top_y_ok = []
                top_x_notOk = []
                top_y_notOk = []
                
                angles = []

                for sa in sensor_angles:
                    if sa-rr < sensor_angles[0]:
                        angles.append(start_angle-rr+(sa-sensor_angles[0]))
                for sa in sensor_angles:
                    angles.append(start_angle+(sa-sensor_angles[0]))
                for sa in sensor_angles:
                    if sa+rr > sensor_angles[-1]:
                        angles.append(start_angle+rr+(sa-sensor_angles[0]))

                #for p in range(self.currentConfig.values['iy']):
                    #if start_angle-rr+2*p*hpfovy < start_angle:
                        #angles.append(start_angle-rr+2*p*hpfovy)
                #for p in range(self.currentConfig.values['iy']):
                    #angles.append(start_angle+2*p*hpfovy)
                #for p in range(self.currentConfig.values['iy']):
                    #if start_angle+rr+2*p*hpfovy > end_angle:
                        #angles.append(start_angle+rr+2*p*hpfovy)

                last_angle = None
                for a in angles:
                    if a < 0.0 and last_angle is not None:
                        #rc = -self.currentConfig.values['height']/math.tan(a)
                        rn = -self.currentConfig.values['height']/math.tan(last_angle)
                        rf = -self.currentConfig.values['height']/math.tan(a)
                        rm = rn+((rf-rn)/2.0)
                        x.append(rm*pan_factor)
                        y.append(rf-rn)
                        if max_y is None:
                            max_y = y[-1]
                        else:
                            max_y = max(max_y, y[-1])
                        if y[-1] > self.currentConfig.values['resolution']:
                            ok.append(False)
                        else:
                            ok.append(True)
                        notOk.append(not ok[-1])
                        for xa in sensor_angles_x:
                            b = xa + math.radians(self.currentConfig.values['pan_angle'])
                            if ok[-1]:
                                top_x_ok.append(math.sin(b)*rm)
                                top_y_ok.append(math.cos(b)*rm)
                            else:
                                top_x_notOk.append(math.sin(b)*rm)
                                top_y_notOk.append(math.cos(b)*rm)
                    last_angle = a

                if z > 1.0:
                    footprint_axes.fill_between(x,y,where=ok,color=bright_green)
                    footprint_axes.fill_between(x,y,where=notOk,color=bright_red)
                    legend_axes.append(matplotlib.pyplot.Rectangle((0,0),1,1,fc=bright_green))
                    footprint_legend_labels.append('footprint < resolution (max zoom)')
                    legend_axes.append(matplotlib.pyplot.Rectangle((0,0),1,1,fc=bright_red))
                    footprint_legend_labels.append('footprint > resolution (max zoom)')
                    geomtry_legend_labels.append('always visible (max zoom)')
                    geomtry_legend_labels.append('sometimes visible (max zoom)')
                    top_axes.plot(top_x_ok,top_y_ok,'.',color=bright_green)
                    top_axes.plot(top_x_notOk,top_y_notOk,'.',color=bright_red)
                else:
                    footprint_axes.fill_between(x,y,where=ok,color=pale_green)
                    footprint_axes.fill_between(x,y,where=notOk,color=pale_red)
                    top_axes.plot(top_x_ok,top_y_ok,'.',color=pale_green)
                    top_axes.plot(top_x_notOk,top_y_notOk,'.',color=pale_red)

                patches = []
                if rr > 0.0:
                    ep = (0.0,self.currentConfig.values['height'])
                    if start_angle-rr < 0.0:
                        nc = (-self.currentConfig.values['height']/math.tan(start_angle-rr),0.0)
                    else:
                        nc = (self.currentConfig.values['range'],self.currentConfig.values['height']+self.currentConfig.values['range']*math.tan(start_angle-rr))
                    if end_angle+rr < 0.0:
                        fc = (-self.currentConfig.values['height']/math.tan(end_angle+rr),0.0)
                    else:
                        fc = (self.currentConfig.values['range'],self.currentConfig.values['height']+self.currentConfig.values['range']*math.tan(end_angle+rr))

                    print (ep,nc,fc)
                    polygon = matplotlib.patches.Polygon((ep,nc,fc), True)
                    patches.append(polygon)

                    
                    x = []
                    y0 = []
                    y1 = []
                    for i in range(1000):
                        x.append(self.currentConfig.values['range']*i/1000.0)
                        y0.append(max(0.0,(x[-1]/pan_factor)*math.tan(start_angle-rr)+self.currentConfig.values['height']))
                        y1.append(max(0.0,(x[-1]/pan_factor)*math.tan(end_angle+rr)+self.currentConfig.values['height']))
                    if z > 1.0:
                        geometry_axes.fill_between(x,y1,y0,color=bright_red)
                    else:
                        geometry_axes.fill_between(x,y1,y0,color=pale_red)


                x = []
                y0 = []
                y1 = []
                for i in range(1000):
                    x.append(self.currentConfig.values['range']*i/1000.0)
                    pan_factor
                    y0.append(max(0.0,x[-1]*math.tan(start_angle+rr)+self.currentConfig.values['height']))
                    y1.append(max(0.0,x[-1]*math.tan(end_angle-rr)+self.currentConfig.values['height']))
                if z > 1.0:
                    geometry_axes.fill_between(x,y1,y0,color=bright_green)
                else:
                    geometry_axes.fill_between(x,y1,y0,color=pale_green)

                p = matplotlib.collections.PatchCollection(patches)
                #geometry_axes.add_collection(p)
                    
                geometry_axes.plot([0,self.currentConfig.values['range']],[0.0,0.0],color=(0.0,0.0,1.0,1.0))


            x = [0, self.currentConfig.values['range']]
            y = [self.currentConfig.values['resolution'],self.currentConfig.values['resolution']]
            legend_axes.append(footprint_axes.plot(x,y,'b'))
            
            footprint_legend_labels.append('target resolution')
            geomtry_legend_labels.append('waterline')

            footprint_axes.set_ylim((0,max_y*2.0))
            footprint_axes.set_xlim((0,self.currentConfig.values['range']))
            footprint_axes.set_xlabel('range (m)')
            footprint_axes.set_ylabel('pixel footprint (m)')
            footprint_axes.set_title('Pixel footprint vs range')
        
            geometry_axes.set_xlim((0,self.currentConfig.values['range']))
            geometry_axes.set_aspect('equal')
            #geometry_axes.set_ylim((0,max(self.currentConfig.values['height']*2.0,self.currentConfig.values['range']*.2)))

            top_axes.set_xlim((-self.currentConfig.values['range'],self.currentConfig.values['range']))
            top_axes.set_ylim((-self.currentConfig.values['range'],self.currentConfig.values['range']))
            top_axes.set_aspect('equal')
            top_axes.set_xlabel('across track range (m)')
            top_axes.set_ylabel('along track range (m)')
            top_axes.set_title('Top down view. Pan angle: {} degrees relative to bow.'.format(self.currentConfig.values['pan_angle']))
            
            
            geometry_axes.set_xlabel('range (m)')
            geometry_axes.set_ylabel('height (m)')
            geometry_axes.set_title('Vertical field of view at tilt of '+str(self.currentConfig.values['tilt_angle']) + ' degrees with ' + str(self.currentConfig.values['roll_range']) + ' degrees of roll')

            footprint_axes.legend(legend_axes,footprint_legend_labels,loc=2)
            geometry_axes.legend(legend_axes,geomtry_legend_labels, loc=2)


        self.plots.draw()


    def updateFromControl(self,ctrl):
        if not self.updating:
            try:
                return float(ctrl.GetValue())
            except ValueError:
                return None

    def OnFixedBaseFOVChecked(self, evt):
        self.enableGUI(True)
                
    def OnImagerSizeXChanged(self, evt):
        x = self.updateFromControl(self.imagerSizeXTextCtrl)
        if x is not None:
            self.currentConfig.values['ix'] = int(x)
            self.updateGUI()

    def OnImagerSizeXMMChanged(self, evt):
        x = self.updateFromControl(self.imagerSizeXMMTextCtrl)
        if x is not None:
            oldValue = self.currentConfig.values['ixmm']
            self.currentConfig.values['ixmm'] = x
            if self.fixedPixelAspectCheckBox.GetValue():
                self.currentConfig.values['iymm'] *= x/oldValue
            if not self.fixedBaseFOVCheckBox.GetValue():
                self.setFX(self.currentConfig.values['fx']*oldValue/x)
            self.updateGUI()
                    
            
    def OnImagerSizeYChanged(self, evt):
        y = self.updateFromControl(self.imagerSizeYTextCtrl)
        if y is not None:
            self.currentConfig.values['iy'] = int(y)
            self.updateGUI()

    def OnImagerSizeYMMChanged(self, evt):
        y = self.updateFromControl(self.imagerSizeYMMTextCtrl)
        if y is not None:
            oldValue = self.currentConfig.values['iymm']
            self.currentConfig.values['iymm'] = y
            if self.fixedPixelAspectCheckBox.GetValue():
                self.currentConfig.values['ixmm'] *= y/oldValue
            if not self.fixedBaseFOVCheckBox.GetValue():
                self.setFY(self.currentConfig.values['fy']*oldValue/y)
            self.updateGUI()
            
    def OnRangeChanged(self, evt):
        r = self.updateFromControl(self.rangeTextCtrl)
        if r is not None:
            self.currentConfig.values['range'] = r
            self.updateGUI()

    def OnHeightChanged(self, evt):
        h = self.updateFromControl(self.heightTextCtrl)
        if h is not None:
            self.currentConfig.values['height'] = h
            self.updateGUI()

    def OnMaxZoomChanged(self, evt):
        z = self.updateFromControl(self.maxZoomTextCtrl)
        if z is not None:
            self.currentConfig.values['max_zoom'] = z
            self.updateGUI()

    def OnResolutionChanged(self, evt):
        r = self.updateFromControl(self.resolutionTextCtrl)
        if r is not None:
            self.currentConfig.values['resolution'] = r
            self.updateGUI()

    def setFX(self,fx,scale = 1.0):
        if fx is not None:
            pr = self.currentConfig.values['fx']/self.currentConfig.values['fy']
            self.currentConfig.values['fx'] = fx/scale
            if self.fixedPixelAspectCheckBox.GetValue():
                self.currentConfig.values['fy'] = self.currentConfig.values['fx']/pr
            self.updateGUI()

    def setFovX(self,fovx,scale = 1.0):
        if fovx is not None:
            self.setFX((self.currentConfig.values['ix']/2.0)/math.tan(math.radians(fovx/2.0)),scale)



    def setFY(self,fy,scale = 1.0):
        if fy is not None:
            pr = self.currentConfig.values['fy']/self.currentConfig.values['fx']
            self.currentConfig.values['fy'] = fy/scale
            if self.fixedPixelAspectCheckBox.GetValue():
                self.currentConfig.values['fx'] = self.currentConfig.values['fy']/pr
            self.updateGUI()

    def setFovY(self,fovy,scale=1.0):
        if fovy is not None:
            self.setFY((self.currentConfig.values['iy']/2.0)/math.tan(math.radians(fovy/2.0)),scale)

    def OnBaseFXChanged(self, evt):
        self.setFX(self.updateFromControl(self.baseFXTextCtrl))

    def OnBaseFXMMChanged(self, evt):
        if self.fixedBaseFOVCheckBox.GetValue():
            x = self.updateFromControl(self.baseFXMMTextCtrl)
            if x is not None:
                pr = self.currentConfig.values['ixmm']/self.currentConfig.values['iymm']
                self.currentConfig.values['ixmm']=x*self.currentConfig.values['ix']/self.currentConfig.values['fx']
                if self.fixedPixelAspectCheckBox.GetValue():
                    self.currentConfig.values['iymm'] = self.currentConfig.values['ixmm']/pr
                self.updateGUI()
        else:
            self.setFX(self.updateFromControl(self.baseFXMMTextCtrl)*self.currentConfig.values['ix']/self.currentConfig.values['ixmm'])
            
        
    def OnBaseFYChanged(self, evt):
        self.setFY(self.updateFromControl(self.baseFYTextCtrl))

    def OnBaseFYMMChanged(self, evt):
        if self.fixedBaseFOVCheckBox.GetValue():
            y = self.updateFromControl(self.baseFYMMTextCtrl)
            if y is not None:
                pr = self.currentConfig.values['iymm']/self.currentConfig.values['ixmm']
                self.currentConfig.values['iymm']=y*self.currentConfig.values['iy']/self.currentConfig.values['fy']
                if self.fixedPixelAspectCheckBox.GetValue():
                    self.currentConfig.values['ixmm'] = self.currentConfig.values['iymm']/pr
                self.updateGUI()
        else:
            self.setFY(self.updateFromControl(self.baseFYMMTextCtrl)*self.currentConfig.values['iy']/self.currentConfig.values['iymm'])
            
    def OnBaseFovXChanged(self, evt):
        self.setFovX(self.updateFromControl(self.baseFovXTextCtrl))

    def OnBaseFovYChanged(self, evt):
        self.setFovY(self.updateFromControl(self.baseFovYTextCtrl))

    def OnMaxFXChanged(self, evt):
        if self.fixedBaseFOVCheckBox.GetValue():
            x = self.updateFromControl(self.maxFXTextCtrl)
            if x is not None:
                self.currentConfig.values['max_zoom'] = x/self.currentConfig.values['fx']
                self.updateGUI()
        else:
            self.setFX(self.updateFromControl(self.maxFXTextCtrl),self.currentConfig.values['max_zoom'])
        
    def OnMaxFXMMChanged(self, evt):
        if self.fixedBaseFOVCheckBox.GetValue():
            x = self.updateFromControl(self.maxFXMMTextCtrl)
            if x is not None:
                self.currentConfig.values['max_zoom'] = x/( self.currentConfig.values['ixmm']*self.currentConfig.values['fx']/self.currentConfig.values['ix'])
                self.updateGUI()
        else:
            self.setFX(self.updateFromControl(self.maxFXMMTextCtrl)*self.currentConfig.values['ix']/self.currentConfig.values['ixmm'],self.currentConfig.values['max_zoom'])
            
    def OnMaxFYChanged(self, evt):
        if self.fixedBaseFOVCheckBox.GetValue():
            y = self.updateFromControl(self.maxFYTextCtrl)
            if y is not None:
                self.currentConfig.values['max_zoom'] = y/self.currentConfig.values['fy']
                self.updateGUI()
        else:
            self.setFY(self.updateFromControl(self.maxFYTextCtrl),self.currentConfig.values['max_zoom'])

    def OnMaxFYMMChanged(self, evt):
        if self.fixedBaseFOVCheckBox.GetValue():
            y = self.updateFromControl(self.maxFYMMTextCtrl)
            if y is not None:
                self.currentConfig.values['max_zoom'] = y/( self.currentConfig.values['iymm']*self.currentConfig.values['fy']/self.currentConfig.values['iy'])
                self.updateGUI()
        else:
            self.setFY(self.updateFromControl(self.maxFYMMTextCtrl)*self.currentConfig.values['iy']/self.currentConfig.values['iymm'],self.currentConfig.values['max_zoom'])
        
    def OnMaxFovXChanged(self, evt):
        if self.fixedBaseFOVCheckBox.GetValue():
            fovx = self.updateFromControl(self.maxFovXTextCtrl)
            if fovx is not None:
                self.currentConfig.values['max_zoom'] = (self.currentConfig.values['ix']/2.0)/math.tan(math.radians(fovx/2.0))/self.currentConfig.values['fx']
                self.updateGUI()
        else:
            self.setFovX(self.updateFromControl(self.maxFovXTextCtrl),self.currentConfig.values['max_zoom'])

    def OnMaxFovYChanged(self, evt):
        if self.fixedBaseFOVCheckBox.GetValue():
            fovy = self.updateFromControl(self.maxFovYTextCtrl)
            if fovy is not None:
                self.currentConfig.values['max_zoom'] = (self.currentConfig.values['iy']/2.0)/math.tan(math.radians(fovy/2.0))/self.currentConfig.values['fy']
                self.updateGUI()
        else:
            self.setFovY(self.updateFromControl(self.maxFovYTextCtrl),self.currentConfig.values['max_zoom'])

    def OnPanAngleChanged(self, evt):
        a = self.updateFromControl(self.panAngleTextCtrl)
        if a is not None:
            self.currentConfig.values['pan_angle'] = a
            self.updateGUI()


    def OnTiltAngleChanged(self, evt):
        a = self.updateFromControl(self.tiltAngleTextCtrl)
        if a is not None:
            self.currentConfig.values['tilt_angle'] = a
            self.updateGUI()

    def OnRollRangeChanged(self, evt):
        rr = self.updateFromControl(self.rollRangeTextCtrl)
        if rr is not None:
            self.currentConfig.values['roll_range'] = rr
            self.updateGUI()

    def OnFileNew(self, evt):
        self.clear()

    def OnFileOpen(self, evt):
        d = wx.FileDialog(self,wildcard='*.xml',style=wx.FD_OPEN)
        ret = d.ShowModal()
        if ret == wx.ID_OK:
            self.open(str(d.GetPath()))

    def OnFileSave(self, evt):
        if self.filename is None:
            self.OnFileSaveAs(evt)
        else:
            self.save(self.filename)

    def OnFileSaveAs(self, evt):
        d = wx.FileDialog(self,wildcard='*.xml',style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        ret = d.ShowModal()
        if ret == wx.ID_OK:
            self.save(str(d.GetPath()))

    def OnSaveGraph(self, evt):
        d = wx.FileDialog(self,wildcard='*.png',style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        ret = d.ShowModal()
        if ret == wx.ID_OK:
            self.plots.get_figure().savefig(str(d.GetPath()))


    def OnConfigComboText(self, evt):
        config = self.configComboBox.GetValue()
        config_id = self.configComboBox.FindString(config)
        if  config_id == wx.NOT_FOUND or self.configComboBox.GetClientData(config_id) != self.currentConfig:
            self.enableGUI(False)
        else:
            self.enableGUI()
            

    def OnConfigComboTextEnter(self, evt):
        config = self.configComboBox.GetValue()
        config_id = self.configComboBox.FindString(config)
        if  config_id == wx.NOT_FOUND:
            if self.currentConfig is not None:
                new_config = Configuration(self.currentConfig)
            else:
                new_config = Configuration()
            self.configComboBox.Append(config,new_config)
            self.setCurrentConfig(new_config)
        else:
            self.setCurrentConfig(self.configComboBox.GetClientData(config_id))

    def OnConfigCombo(self, evt):
        config_id = self.configComboBox.GetSelection()
        if  config_id == wx.NOT_FOUND:
            self.setCurrentConfig(None)
        else:
            self.setCurrentConfig(self.configComboBox.GetClientData(config_id))

    def OnConfigDescriptionText(self, evt):
        if not self.updating:
            self.currentConfig.description = self.configDescriptionTextCtrl.GetValue()
            #self.updatePlots()

    def OnConfigDescriptionTextEnter(self, evt):
        self.updatePlots()
        evt.Skip()

if __name__ == "__main__":
    app = wx.App()
    fname = None
    if len(sys.argv) == 2:
        fname = sys.argv[1]
    geoCamPlanner = GeoCamPlanner(fname)
    app.SetTopWindow(geoCamPlanner)
    geoCamPlanner.Show()
    app.MainLoop()
