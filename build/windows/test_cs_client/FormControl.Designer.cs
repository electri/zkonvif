namespace test_cs_client
{
    partial class FormControl
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.labelIp = new System.Windows.Forms.Label();
            this.comboBoxIp = new System.Windows.Forms.ComboBox();
            this.labelPort = new System.Windows.Forms.Label();
            this.menuStrip1 = new System.Windows.Forms.MenuStrip();
            this.comboBoxPort = new System.Windows.Forms.ComboBox();
            this.SuspendLayout();
            // 
            // labelIp
            // 
            this.labelIp.AutoSize = true;
            this.labelIp.Location = new System.Drawing.Point(29, 41);
            this.labelIp.Name = "labelIp";
            this.labelIp.Size = new System.Drawing.Size(47, 12);
            this.labelIp.TabIndex = 0;
            this.labelIp.Text = "ip地址:";
            // 
            // comboBoxIp
            // 
            this.comboBoxIp.FormattingEnabled = true;
            this.comboBoxIp.Location = new System.Drawing.Point(82, 33);
            this.comboBoxIp.Name = "comboBoxIp";
            this.comboBoxIp.Size = new System.Drawing.Size(167, 20);
            this.comboBoxIp.TabIndex = 1;
            // 
            // labelPort
            // 
            this.labelPort.AutoSize = true;
            this.labelPort.Location = new System.Drawing.Point(271, 41);
            this.labelPort.Name = "labelPort";
            this.labelPort.Size = new System.Drawing.Size(47, 12);
            this.labelPort.TabIndex = 2;
            this.labelPort.Text = "端口号:";
            // 
            // menuStrip1
            // 
            this.menuStrip1.Location = new System.Drawing.Point(0, 0);
            this.menuStrip1.Name = "menuStrip1";
            this.menuStrip1.Size = new System.Drawing.Size(742, 24);
            this.menuStrip1.TabIndex = 3;
            this.menuStrip1.Text = "menuStrip1";
            // 
            // comboBoxPort
            // 
            this.comboBoxPort.FormattingEnabled = true;
            this.comboBoxPort.Location = new System.Drawing.Point(337, 33);
            this.comboBoxPort.Name = "comboBoxPort";
            this.comboBoxPort.Size = new System.Drawing.Size(121, 20);
            this.comboBoxPort.TabIndex = 4;
            // 
            // FormControl
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(742, 558);
            this.Controls.Add(this.comboBoxPort);
            this.Controls.Add(this.labelPort);
            this.Controls.Add(this.comboBoxIp);
            this.Controls.Add(this.labelIp);
            this.Controls.Add(this.menuStrip1);
            this.MainMenuStrip = this.menuStrip1;
            this.Name = "FormControl";
            this.Text = "FormControl";
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Label labelIp;
        private System.Windows.Forms.ComboBox comboBoxIp;
        private System.Windows.Forms.Label labelPort;
        private System.Windows.Forms.MenuStrip menuStrip1;
        private System.Windows.Forms.ComboBox comboBoxPort;
    }
}