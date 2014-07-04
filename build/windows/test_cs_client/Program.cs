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
        }

        static void test_event(string url)
        {
            Console.WriteLine("==== test event interface ====");

            /// TODO: 测试事件接口 ...

            Console.WriteLine("------------ end -------------");
        }
    }
}
