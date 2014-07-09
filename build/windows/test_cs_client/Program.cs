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
            if (args.Length == 0) {
                MessageBox.Show("必须在命令行启动，并且设置参数为 http://.... 格式，指向dm");
                return;
            }

            /// TODO: 这里输入多个参数更合理，用于指定测试的对象 ...

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            string dm_url = "http://172.16.1.111:10000";
            if (args.Length > 0)
                dm_url = args[0];

            zonvif_dm.DeviceBinding dm = new zonvif_dm.DeviceBinding();
            dm.Url = dm_url;

            string url0 = null;
            zonvif_dm.Service[] services = dm.GetServices(false);
            foreach (zonvif_dm.Service s in services) {
                string url = s.XAddr;
                string ns = s.Namespace;
                if (url != null && ns != null) {
                    Console.WriteLine("INFO: Service '" + s.Namespace + "', url='" + url + "'");
                    if (ns == "ptz") {
                        // FIXME: 仅仅测试云台模块 ...
                        url0 = url;
                        break;
                    }
                }
            }

            /// TODO: 根据测试对象，决定启动的窗体 ...
            Application.Run(new FormControl(url0));
        }
    }
}
