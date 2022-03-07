# -*- coding:utf-8 -*-
"""
Created on Dec 18, 2017

@author: Filip
"""


class QTangoColors(object):
    def __init__(self):
        self.backgroundColor = '#000000'
        self.primaryColor0 = '#ff9900'
        self.primaryColor1 = '#ffcc66'
        self.primaryColor2 = '#feff99'
        self.primaryColor3 = '#bb6622'
        self.primaryColor4 = '#aa5533'
        self.primaryColor5 = '#882211'
        self.secondaryColor0 = '#66cbff'
        self.secondaryColor1 = '#3399ff'
        self.secondaryColor2 = '#99cdff'
        self.secondaryColor3 = '#3366cc'
        self.secondaryColor4 = '#000088'
        self.tertiaryColor0 = '#cc99cc'
        self.tertiaryColor1 = '#cc6699'
        self.tertiaryColor2 = '#cc6666'
        self.tertiaryColor3 = '#664466'
        self.tertiaryColor4 = '#9977aa'

        self.faultColor = '#ff0000'
        self.alarmColor2 = '#ffffff'
        self.warnColor = '#a35918'
        self.alarmColor = '#ff0000'
        self.warnColor2 = '#ffcc33'
        self.onColor = '#99dd66'
        self.offColor = '#ffffff'
        self.standbyColor = '#9c9cff'
        self.unknownColor = '#45616f'
        self.disableColor = '#ff00ff'
        self.movingColor = '#feff99'
        self.runningColor = '#66cbff'
        self.closeColor = self.offColor
        self.openColor = self.runningColor

        self.validColor = self.secondaryColor0
        self.invalidColor = self.unknownColor
        self.changingColor = self.secondaryColor1

        self.legend_color_list = [self.secondaryColor0,
                                  self.primaryColor2,
                                  self.tertiaryColor1,
                                  self.secondaryColor3,
                                  self.primaryColor3,
                                  self.tertiaryColor4,
                                  self.primaryColor5,
                                  self.secondaryColor4,
                                  self.tertiaryColor3]


class QTangoSizes(object):
    def __init__(self):
        self.barHeight = 30
        self.barWidth = 20
        self.readAttributeWidth = 200
        self.readAttributeHeight = 200
        self.writeAttributeWidth = 280
        self.trendWidth = 100
        self.fontSize = 12
        self.fontType = 'Calibri'
        self.fontStretch = 75
        self.fontWeight = 50


backgroundColor = '#000000'
primaryColor0 = '#ff9900'
primaryColor1 = '#ffcc66'
primaryColor2 = '#feff99'
secondaryColor0 = '#66cbff'
secondaryColor1 = '#3399ff'
secondaryColor2 = '#99cdff'

faultColor = '#ff0000'
alarmColor = '#f7bd5a'
onColor = '#99dd66'
offColor = '#ffffff'
standbyColor = '#9c9cff'
unknownColor = '#45616f'
disableColor = '#ff00ff'
