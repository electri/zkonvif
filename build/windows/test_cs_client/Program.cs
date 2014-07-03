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
                    if (ns == "event")
                        test_event(url);

                }
            }
        }

        static void test_ptz(string url)
        {

        }

        static void test_event(string url)
        {

        }
    }
}
