using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Xml.Serialization;
using System.Runtime.Remoting.Metadata.W3cXsd2001;
using System.Windows.Forms;

namespace test_cs_client
{
            /// <summary>
        /// The main entry point for the application.
        /// </summary>
    class Program
    {
         [STAThread]
        static void Main(string[] args)
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new FormControl());

            //string dm_url = "http://172.16.1.111:10000";
            //if (args.Length > 0)
            //    dm_url = args[0];

            //zonvif_dm.DeviceBinding dm = new zonvif_dm.DeviceBinding();
            //dm.Url = dm_url;

            //zonvif_dm.Service[] services = dm.GetServices(false);
            //foreach (zonvif_dm.Service s in services) {
            //    string url = s.XAddr;
            //    string ns = s.Namespace;
            //    if (url != null && ns != null) {
            //        Console.WriteLine("INFO: Service '" + s.Namespace + "', url='" + url + "'");

            //        if (ns == "ptz")
            //            test_ptz(url);
            //        else if (ns == "event")
            //            test_event(url);
            //        else
            //            Console.WriteLine("WARNING: Unknown ns '" + ns + "'!");
            //    }
           // }
        }
    }
}
