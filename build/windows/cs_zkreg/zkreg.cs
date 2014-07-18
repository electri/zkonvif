using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Threading;

namespace cs_zkreg
{
    public class zkreg
    {
        static public void reg(string ns, string url, string desc, string service_name)
        {
            reg0(ns, url, desc, service_name);
        }

        static public void unreg()
        {
            unreg0();
        }

        //////////////////////////////////////////////////////////////////////////////////////////////
        static string ns_, url_, desc_, service_name_;
        static bool quit_ = false;
        static Thread th_ = null;
        static AutoResetEvent evt = new AutoResetEvent(false);

        static void reg0(string ns, string url, string desc, string service_name)
        {
            if (th_ != null)
                return;

            ns_ = ns;
            url_ = url;
            desc_ = desc;
            if (service_name == null) {
                service_name_ = System.Diagnostics.Process.GetCurrentProcess().MainModule.FileName;
            }
            else {
                service_name_ = service_name;
            }

            quit_ = false;
            th_ = new Thread(new ThreadStart(run));
            th_.Start();
        }

        static void unreg0()
        {
            if (th_ != null) {
                quit_ = true;
                evt.Set();
                th_.Join();
            }
        }

        static void run()
        {
            int id = -1;
            string sid;
            bool reged = false;

            while (!quit_) {
                if (!reged) {
                    reged = reg(ref id, out sid);
                }

                if (evt.WaitOne(10000))
                    continue;

                if (reged) {
                    hb(id);
                }
            }

            if (reged) {
                unreg(id);
            }
        }

        static string endp()
        {
            return "http://localhost:10000";
        }

        static bool reg(ref int id, out string sid)
        {
            sid = null;
            zonvif_dm.DeviceBinding db = new zonvif_dm.DeviceBinding();
            db.Url = endp();
            zonvif_dm.ZonekeyDMServRegisterType req = new zonvif_dm.ZonekeyDMServRegisterType();
            req.ns = ns_;
            req.desc = desc_;
            req.url = url_;
            req.addr = service_name_;

            //try {
                //zonvif_dm.ZonekeyDMServRegisterResponseType res = db.Reg
            //}

            return false;
        }

        static void hb(int id)
        {

        }

        static void unreg(int id)
        {

        }
    }
}
