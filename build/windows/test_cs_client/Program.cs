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
                test_ptz_0(ptz, node);
            }

            Console.WriteLine("------------ end -------------");
        }

        static void test_ptz_0(zonvif_ptz.PTZBinding ptz, zonvif_ptz.PTZNode node)
        {
            Console.WriteLine(string.Format("INFO: testing ptz: token '{0}', name '{1}'", node.token, node.Name));

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

            // 设置云台指向：
            zonvif_ptz.PTZVector pos = new zonvif_ptz.PTZVector();
            pos.PanTilt.x = 100;
            pos.PanTilt.y = 0;
            pos.Zoom = null;

            // 速度 ...
            zonvif_ptz.PTZSpeed speed = new zonvif_ptz.PTZSpeed();
            speed.PanTilt.x = (float)30.0;
            speed.PanTilt.y = (float)30.0;
            speed.Zoom.x = (float)1.0;
            ptz.AbsoluteMove(node.token, pos, speed);

            Console.WriteLine(string.Format("\tAbsoluteMove: pos={0}, {1}", pos.PanTilt.x, pos.PanTilt.y));

            // 循环获取云台指向，多遍
            for (int i = 0; i < 3; i++) {
                zonvif_ptz.PTZStatus status = ptz.GetStatus(node.token);
                Console.WriteLine(string.Format("\t[#{3}] GetStatus: pos={0}, {1}, {2}", status.Position.PanTilt.x, status.Position.PanTilt.y, status.Position.Zoom.x, i));
                System.Threading.Thread.Sleep(100);  // FIXME: 让 AbsoluteMove 执行完成？ .
            }

            // 设置 zoom
            pos.PanTilt = null;
            pos.Zoom.x = (float)5000.0;
            ptz.AbsoluteMove(node.token, pos, speed);

            // 循环获取 zoom
            for (int i = 0; i < 10; i++) {
                zonvif_ptz.PTZStatus status = ptz.GetStatus(node.token);
                Console.WriteLine(string.Format("\t[#{3}] GetStatus: pos={0}, {1}, {2}", status.Position.PanTilt.x, status.Position.PanTilt.y, status.Position.Zoom.x, i));
                System.Threading.Thread.Sleep(100);  // FIXME: 让 AbsoluteMove 执行完成？ .
            }

            // 上下左右转动
            
        }

        static void test_event(string url)
        {
            Console.WriteLine("==== test event interface ====");

            /// TODO: 测试事件接口 ...

            Console.WriteLine("------------ end -------------");
        }
    }
}
