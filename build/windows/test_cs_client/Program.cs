using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace test_cs_client
{
    class Program
    {
        static void Main(string[] args)
        {
            string dm_url = "http://localhost:10000";
            if (args.Length > 0)
                dm_url = args[0];

            zonvif_dm.DeviceBinding dm = new zonvif_dm.DeviceBinding();
            dm.Url = dm_url;

            zonvif_dm.Service[] services = dm.GetServices(false);
            foreach (zonvif_dm.Service s in services) {
                string url = s.XAddr;
                string ns = s.Namespace;
                if (url != null && ns != null) {
                    Console.WriteLine("INFO: Service '" + s.Namespace + "', url='" + url + "'");

                    if (ns == "ptz")
                        test_ptz(url);
                    else if (ns == "event")
                        test_event(url);
                    else
                        Console.WriteLine("WARNING: Unknown ns '" + ns + "'!");
                }
            }
        }

        static void test_ptz(string url)
        {
            Console.WriteLine("===== test ptz interface =====");

            zonvif_ptz.PTZBinding ptz = new zonvif_ptz.PTZBinding();
            ptz.Url = url;

            // GetNodes
            zonvif_ptz.PTZNode []nodes = ptz.GetNodes();
            Console.WriteLine(string.Format("There are {0} ptzs", nodes.Length));
            foreach (zonvif_ptz.PTZNode node in nodes) {
                zonvif_ptz.PTZNode n = ptz.GetNode(node.token);
                test_ptz_0(ptz, n);
            }

            Console.WriteLine("------------ end -------------");
        }

        static void test_ptz_0(zonvif_ptz.PTZBinding ptz, zonvif_ptz.PTZNode node)
        {
            Console.WriteLine(string.Format("INFO: testing ptz: token '{0}', name '{1}'", node.token, node.Name));

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
            pos.PanTilt.x = (float)100.0;
            pos.PanTilt.y = (float)100.0;

            // 设置云台指向：
            ptz.AbsoluteMove(node.token, pos, speed);

            // 连续数次调用 ...
            for (int i = 0; i < 3; i++)
            {
                zonvif_ptz.PTZStatus status = ptz.GetStatus(node.token);
                Console.WriteLine(string.Format("\t\t[#{0}]: pos={1}, {2}, {3}", i, status.Position.PanTilt.x, status.Position.PanTilt.y, status.Position.Zoom.x));

                System.Threading.Thread.Sleep(100);
            }


        }

        static void test_event(string url)
        {
            Console.WriteLine("==== test event interface ====");

            /// TODO: 测试事件接口 ...

            Console.WriteLine("------------ end -------------");
        }
    }
}
