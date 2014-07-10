using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace test_cs_client
{
    public partial class ucPtzControl : UserControl
    {
        zonvif_ptz.PTZBinding ptz_ = null;
        string token_;

        public ucPtzControl(zonvif_ptz.PTZBinding ptz, string token)
        {
            // FIXME: 这些逻辑放在这里不是很好，照理说，uc 应该仅仅关注界面事件即可，但这样做更方便，呵呵
            ptz_ = ptz;
            token_ = token;
            InitializeComponent();
        }

        public delegate void PtzButtonEventType(int who, int up);
        public event PtzButtonEventType PtzButtonEvent;

        private void button1_MouseDown(object sender, MouseEventArgs e)
        {
            zonvif_ptz.PTZSpeed speed = new zonvif_ptz.PTZSpeed();
            speed.PanTilt = new zonvif_ptz.Vector2D();
            speed.PanTilt.x = 0; speed.PanTilt.y = 2;  // 上

            ptz_.ContinuousMove(token_, speed, null);
        }

        private void button1_MouseUp(object sender, MouseEventArgs e)
        {
            ptz_.Stop(token_, true, false, true, false);
        }

        private void button3_MouseDown(object sender, MouseEventArgs e)
        {
            zonvif_ptz.PTZSpeed speed = new zonvif_ptz.PTZSpeed();
            speed.PanTilt = new zonvif_ptz.Vector2D();
            speed.PanTilt.x = -2; speed.PanTilt.y = 0;  // 左

            ptz_.ContinuousMove(token_, speed, null);
        }

        private void button3_MouseUp(object sender, MouseEventArgs e)
        {
            ptz_.Stop(token_, true, false, true, false);
        }

        private void button2_MouseDown(object sender, MouseEventArgs e)
        {
            zonvif_ptz.PTZSpeed speed = new zonvif_ptz.PTZSpeed();
            speed.PanTilt = new zonvif_ptz.Vector2D();
            speed.PanTilt.x = 0; speed.PanTilt.y = -2;  // 下

            ptz_.ContinuousMove(token_, speed, null);
        }

        private void button2_MouseUp(object sender, MouseEventArgs e)
        {
            ptz_.Stop(token_, true, false, true, false);
        }

        private void button4_MouseDown(object sender, MouseEventArgs e)
        {
            zonvif_ptz.PTZSpeed speed = new zonvif_ptz.PTZSpeed();
            speed.PanTilt = new zonvif_ptz.Vector2D();
            speed.PanTilt.x = 2; speed.PanTilt.y = 0;  // 右

            ptz_.ContinuousMove(token_, speed, null);
        }

        private void button4_MouseUp(object sender, MouseEventArgs e)
        {
            ptz_.Stop(token_, true, false, true, false);
        }

        private void button5_Click(object sender, EventArgs e)
        {
            // 设置预置位 1

            string t = "1";
            ptz_.SetPreset(token_, null, ref t);
        }

        private void button6_Click(object sender, EventArgs e)
        {
            // 到预置位 1

            string t = "1";
            ptz_.GotoPreset(token_, t, null);
        }

        private void button7_Click(object sender, EventArgs e)
        {
            // 删除预置位 1
            string t = "1";
            ptz_.RemovePreset(token_, t);
        }
    }
}
