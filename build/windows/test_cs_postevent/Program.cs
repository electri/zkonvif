using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace test_cs_postevent
{
    class Program
    {
        static void Main(string[] args)
        {
            zonvif_evt.PostEventBinding peb = new zonvif_evt.PostEventBinding();
            peb.Url = "http://localhost:10001";
            peb.LocalPostEvent("media", "112233445566", -1, "视频源丢失");
            Console.WriteLine("end!");
        }
    }
}
