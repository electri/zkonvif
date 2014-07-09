using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace test_cs_client
{
    public partial class FormControl : Form
    {
        public FormControl()
        {
            InitializeComponent();
        }

        private void test_ptz(string url)
        {
            Console.WriteLine("===== test ptz interface =====");

            zonvif_ptz.PTZBinding ptz = new zonvif_ptz.PTZBinding();
            ptz.Url = url;

            // GetNodes
            zonvif_ptz.PTZNode[] nodes = ptz.GetNodes();
            Console.WriteLine(string.Format("There are {0} ptzs", nodes.Length));
            foreach (zonvif_ptz.PTZNode node in nodes)
            {
                zonvif_ptz.PTZNode n = ptz.GetNode(node.token);
                test_ptz_AbsoluteMove(ptz, n);
                //test_ptz_move(ptz, n);
            }

            Console.WriteLine("------------ end -------------");
        }

        private void test_ptz_move(zonvif_ptz.PTZBinding ptz, zonvif_ptz.PTZNode node)
        {
            Console.WriteLine(string.Format("INFO: testing ptz move"));
            zonvif_ptz.PTZSpeed speed = new zonvif_ptz.PTZSpeed();
            speed.PanTilt = new zonvif_ptz.Vector2D();

            speed.Zoom = new zonvif_ptz.Vector1D();
            speed.Zoom.x = (float)7.0;
            long timeout = 1000;
            TimeSpan ts = new TimeSpan(timeout);

            speed.PanTilt.x = 40;
            speed.PanTilt.y = 0;
            ptz.ContinuousMove(node.token, speed, null);
            System.Threading.Thread.Sleep(200);
            ptz.Stop(node.token, false, false, false, false);

            System.Threading.Thread.Sleep(200);

            speed.PanTilt.x = -40;
            speed.PanTilt.y = 0;
            ptz.ContinuousMove(node.token, speed, null);
            System.Threading.Thread.Sleep(200);
            ptz.Stop(node.token, false, false, false, false);

            System.Threading.Thread.Sleep(200);

            speed.PanTilt.x = 0;
            speed.PanTilt.y = 40;
            ptz.ContinuousMove(node.token, speed, null);
            System.Threading.Thread.Sleep(200);
            ptz.Stop(node.token, false, false, false, false);

            System.Threading.Thread.Sleep(200);

            speed.PanTilt.x = 0;
            speed.PanTilt.y = -40;
            ptz.ContinuousMove(node.token, speed, null);
            System.Threading.Thread.Sleep(200);
            ptz.Stop(node.token, false, false, false, false);
            System.Threading.Thread.Sleep(200);
        }

        private void test_ptz_AbsoluteMove(zonvif_ptz.PTZBinding ptz, zonvif_ptz.PTZNode node)
        {
            Console.WriteLine(string.Format("INFO: testing ptz: token '{0}', name '{1}'", node.token, node.Name));

            double scale = ptz.GetScales(node.token);
            /*
            // Configuration 
            zonvif_ptz.PTZConfiguration cfg = ptz.GetConfiguration(node.token);
            Console.WriteLine(string.Format("\tConfiguration: of token '{0}'", cfg.NodeToken));
            if (cfg.DefaultPTZSpeed != null) {
                Console.WriteLine(string.Format("\t\tDefaultPTZSpeed: {0}, {1}, {2}", cfg.DefaultPTZSpeed.PanTilt.x, 
                    cfg.DefaultPTZSpeed.PanTilt.y, cfg.DefaultPTZSpeed.Zoom.x));
            }
            if (cfg.DefaultAbsolutePantTiltPositionSpace != null) {
                Console.WriteLine(string.Format("\t\tDefaultAbsolutePanTiltPositionSpace: {0}", cfg.DefaultAbsolutePantTiltPositionSpace));
            }
             */

            zonvif_ptz.PTZSpeed speed = new zonvif_ptz.PTZSpeed();
            speed.PanTilt = new zonvif_ptz.Vector2D();
            speed.PanTilt.x = 10;
            speed.PanTilt.y = 10;
            speed.Zoom = new zonvif_ptz.Vector1D();
            speed.Zoom.x = 1;

            zonvif_ptz.PTZVector pos = new zonvif_ptz.PTZVector();
            pos.PanTilt = new zonvif_ptz.Vector2D();
            pos.PanTilt.x = (float)300.0;
            pos.PanTilt.y = (float)300.0;

            // 设置云台指向：
            ptz.AbsoluteMove(node.token, pos, speed);
            System.Threading.Thread.Sleep(200);
            //Console.WriteLine("Scale : {0}", scale.ToString());
            zonvif_ptz.ZonekeyPtzParamType ptzParams = ptz.GetPtzParams(node.token);
            Console.WriteLine(string.Format("PtzParams: {0}, {1}, {2}, {3}, {4}", ptzParams.f,
                ptzParams.pan_max_va, ptzParams.pan_min_angle, ptzParams.tilt_max_va, ptzParams.tilt_min_angle));

            // 连续数次调用 ...
            for (int i = 0; i < 3; i++)
            {
                zonvif_ptz.PTZStatus status = ptz.GetStatus(node.token);
                Console.WriteLine(string.Format("\t\t[#{0}]: pos={1}, {2}, {3}", i, status.Position.PanTilt.x, status.Position.PanTilt.y, status.Position.Zoom.x));

                System.Threading.Thread.Sleep(100);
            }
        }

        private void test_event(string url)
        {
            Console.WriteLine("==== test event interface ====");

            /// TODO: 测试事件接口 ...

            Console.WriteLine("------------ end -------------");
        }
    }
}
