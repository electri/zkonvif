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
        string url_ = null;

        public FormControl(string url)
        {
            url_ = url;
            InitializeComponent();
        }

        private void FormControl_Load(object sender, EventArgs e)
        {
            zonvif_ptz.PTZBinding ptz = new zonvif_ptz.PTZBinding();
            ptz.Url = url_;

            // GetNodes
            zonvif_ptz.PTZNode[] nodes = ptz.GetNodes();
            Console.WriteLine(string.Format("There are {0} ptzs", nodes.Length));

            if (nodes.Length == 0) {
                MessageBox.Show("没有找到需要测试的云台服务 ....");
            }
            else {
                foreach (zonvif_ptz.PTZNode node in nodes) {
                    TabPage tc = new TabPage(node.token);
                    tc.Tag = node;

                    ucPtzControl pc = new ucPtzControl(ptz, node.token);
                    tc.Controls.Add(pc);
                    pc.Dock = DockStyle.Fill;

                    tabCont.TabPages.Add(tc);
                }
            }
        }
    }
}
