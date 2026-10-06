using MissionPlanner.Utilities;
namespace MissionPlanner.Controls
{
    partial class SerialOutputPass
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
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(SerialOutputPass));
            this.gbAddConnection = new System.Windows.Forms.GroupBox();
            this.tableLayoutPanel1 = new System.Windows.Forms.TableLayoutPanel();
            this.lblType = new System.Windows.Forms.Label();
            this.cmbType = new System.Windows.Forms.ComboBox();
            this.lblDirection = new System.Windows.Forms.Label();
            this.cmbDirection = new System.Windows.Forms.ComboBox();
            this.lblPort = new System.Windows.Forms.Label();
            this.txtPort = new System.Windows.Forms.TextBox();
            this.lblExtra = new System.Windows.Forms.Label();
            this.txtExtra = new System.Windows.Forms.TextBox();
            this.chkWriteAccess = new System.Windows.Forms.CheckBox();
            this.btnAdd = new MissionPlanner.Controls.MyButton();
            this.gbConnections = new System.Windows.Forms.GroupBox();
            this.dgvConnections = new System.Windows.Forms.DataGridView();
            this.colType = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colDirection = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colAddress = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colStatus = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colWrite = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.colStop = new System.Windows.Forms.DataGridViewButtonColumn();
            this.gbLog = new System.Windows.Forms.GroupBox();
            this.btnClear = new System.Windows.Forms.Button();
            this.txtLog = new System.Windows.Forms.TextBox();
            this.gbAddConnection.SuspendLayout();
            this.tableLayoutPanel1.SuspendLayout();
            this.gbConnections.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dgvConnections)).BeginInit();
            this.gbLog.SuspendLayout();
            this.SuspendLayout();
            //
            // gbAddConnection
            //
            this.gbAddConnection.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left)
            | System.Windows.Forms.AnchorStyles.Right)));
            this.gbAddConnection.Controls.Add(this.tableLayoutPanel1);
            this.gbAddConnection.Location = new System.Drawing.Point(12, 12);
            this.gbAddConnection.Name = "gbAddConnection";
            this.gbAddConnection.Size = new System.Drawing.Size(560, 85);
            this.gbAddConnection.TabIndex = 0;
            this.gbAddConnection.TabStop = false;
            this.gbAddConnection.Text = UiText.Translate("Add Connection");
            //
            // tableLayoutPanel1
            //
            this.tableLayoutPanel1.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
            | System.Windows.Forms.AnchorStyles.Left)
            | System.Windows.Forms.AnchorStyles.Right)));
            this.tableLayoutPanel1.ColumnCount = 6;
            this.tableLayoutPanel1.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 60F));
            this.tableLayoutPanel1.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 90F));
            this.tableLayoutPanel1.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 65F));
            this.tableLayoutPanel1.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 100F));
            this.tableLayoutPanel1.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 100F));
            this.tableLayoutPanel1.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 110F));
            this.tableLayoutPanel1.Controls.Add(this.lblType, 0, 0);
            this.tableLayoutPanel1.Controls.Add(this.cmbType, 1, 0);
            this.tableLayoutPanel1.Controls.Add(this.lblDirection, 2, 0);
            this.tableLayoutPanel1.Controls.Add(this.cmbDirection, 3, 0);
            this.tableLayoutPanel1.Controls.Add(this.lblPort, 0, 1);
            this.tableLayoutPanel1.Controls.Add(this.txtPort, 1, 1);
            this.tableLayoutPanel1.Controls.Add(this.lblExtra, 2, 1);
            this.tableLayoutPanel1.Controls.Add(this.txtExtra, 3, 1);
            this.tableLayoutPanel1.Controls.Add(this.chkWriteAccess, 4, 1);
            this.tableLayoutPanel1.Controls.Add(this.btnAdd, 5, 0);
            this.tableLayoutPanel1.Location = new System.Drawing.Point(6, 16);
            this.tableLayoutPanel1.Name = "tableLayoutPanel1";
            this.tableLayoutPanel1.RowCount = 2;
            this.tableLayoutPanel1.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 50F));
            this.tableLayoutPanel1.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 50F));
            this.tableLayoutPanel1.Size = new System.Drawing.Size(548, 60);
            this.tableLayoutPanel1.TabIndex = 0;
            //
            // lblType
            //
            this.lblType.Anchor = System.Windows.Forms.AnchorStyles.Left;
            this.lblType.AutoSize = true;
            this.lblType.Location = new System.Drawing.Point(3, 8);
            this.lblType.Name = "lblType";
            this.lblType.Size = new System.Drawing.Size(34, 13);
            this.lblType.TabIndex = 0;
            this.lblType.Text = UiText.Translate("Type:");
            //
            // cmbType
            //
            this.cmbType.Anchor = System.Windows.Forms.AnchorStyles.Left;
            this.cmbType.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cmbType.FormattingEnabled = true;
            this.cmbType.Items.AddRange(new object[] {
            "TCP",
            "UDP",
            "Serial"});
            this.cmbType.Location = new System.Drawing.Point(63, 4);
            this.cmbType.Name = "cmbType";
            this.cmbType.Size = new System.Drawing.Size(80, 21);
            this.cmbType.TabIndex = 1;
            this.cmbType.SelectedIndexChanged += new System.EventHandler(this.cmbType_SelectedIndexChanged);
            //
            // lblDirection
            //
            this.lblDirection.Anchor = System.Windows.Forms.AnchorStyles.Left;
            this.lblDirection.AutoSize = true;
            this.lblDirection.Location = new System.Drawing.Point(153, 8);
            this.lblDirection.Name = "lblDirection";
            this.lblDirection.Size = new System.Drawing.Size(52, 13);
            this.lblDirection.TabIndex = 2;
            this.lblDirection.Text = UiText.Translate("Direction:");
            //
            // cmbDirection
            //
            this.cmbDirection.Anchor = System.Windows.Forms.AnchorStyles.Left;
            this.cmbDirection.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cmbDirection.FormattingEnabled = true;
            this.cmbDirection.Items.AddRange(new object[] {
            "Inbound",
            "Outbound"});
            this.cmbDirection.Location = new System.Drawing.Point(218, 4);
            this.cmbDirection.Name = "cmbDirection";
            this.cmbDirection.Size = new System.Drawing.Size(90, 21);
            this.cmbDirection.TabIndex = 3;
            this.cmbDirection.SelectedIndexChanged += new System.EventHandler(this.cmbDirection_SelectedIndexChanged);
            //
            // lblPort
            //
            this.lblPort.Anchor = System.Windows.Forms.AnchorStyles.Left;
            this.lblPort.AutoSize = true;
            this.lblPort.Location = new System.Drawing.Point(3, 38);
            this.lblPort.Name = "lblPort";
            this.lblPort.Size = new System.Drawing.Size(29, 13);
            this.lblPort.TabIndex = 4;
            this.lblPort.Text = UiText.Translate("Port:");
            //
            // txtPort
            //
            this.txtPort.Anchor = System.Windows.Forms.AnchorStyles.Left;
            this.txtPort.Location = new System.Drawing.Point(63, 35);
            this.txtPort.Name = "txtPort";
            this.txtPort.Size = new System.Drawing.Size(80, 20);
            this.txtPort.TabIndex = 5;
            //
            // lblExtra
            //
            this.lblExtra.Anchor = System.Windows.Forms.AnchorStyles.Left;
            this.lblExtra.AutoSize = true;
            this.lblExtra.Location = new System.Drawing.Point(153, 38);
            this.lblExtra.Name = "lblExtra";
            this.lblExtra.Size = new System.Drawing.Size(32, 13);
            this.lblExtra.TabIndex = 6;
            this.lblExtra.Text = UiText.Translate("Host:");
            //
            // txtExtra
            //
            this.txtExtra.Anchor = System.Windows.Forms.AnchorStyles.Left;
            this.txtExtra.Location = new System.Drawing.Point(218, 35);
            this.txtExtra.Name = "txtExtra";
            this.txtExtra.Size = new System.Drawing.Size(90, 20);
            this.txtExtra.TabIndex = 7;
            //
            // chkWriteAccess
            //
            this.chkWriteAccess.Anchor = System.Windows.Forms.AnchorStyles.Left;
            this.chkWriteAccess.AutoSize = true;
            this.chkWriteAccess.Location = new System.Drawing.Point(318, 36);
            this.chkWriteAccess.Name = "chkWriteAccess";
            this.chkWriteAccess.Size = new System.Drawing.Size(50, 17);
            this.chkWriteAccess.TabIndex = 8;
            this.chkWriteAccess.Text = UiText.Translate("Write");
            this.chkWriteAccess.UseVisualStyleBackColor = true;
            //
            // btnAdd
            //
            this.btnAdd.Anchor = System.Windows.Forms.AnchorStyles.None;
            this.tableLayoutPanel1.SetRowSpan(this.btnAdd, 2);
            this.btnAdd.Location = new System.Drawing.Point(444, 18);
            this.btnAdd.Name = "btnAdd";
            this.btnAdd.Size = new System.Drawing.Size(98, 24);
            this.btnAdd.TabIndex = 9;
            this.btnAdd.Text = UiText.Translate("Add Connection");
            this.btnAdd.UseVisualStyleBackColor = true;
            this.btnAdd.Click += new System.EventHandler(this.btnAdd_Click);
            //
            // gbConnections
            //
            this.gbConnections.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left)
            | System.Windows.Forms.AnchorStyles.Right)));
            this.gbConnections.Controls.Add(this.dgvConnections);
            this.gbConnections.Location = new System.Drawing.Point(12, 103);
            this.gbConnections.Name = "gbConnections";
            this.gbConnections.Size = new System.Drawing.Size(560, 160);
            this.gbConnections.TabIndex = 1;
            this.gbConnections.TabStop = false;
            this.gbConnections.Text = UiText.Translate("Active Connections");
            //
            // dgvConnections
            //
            this.dgvConnections.AllowUserToAddRows = false;
            this.dgvConnections.AllowUserToDeleteRows = false;
            this.dgvConnections.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
            | System.Windows.Forms.AnchorStyles.Left)
            | System.Windows.Forms.AnchorStyles.Right)));
            this.dgvConnections.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dgvConnections.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.colType,
            this.colDirection,
            this.colAddress,
            this.colStatus,
            this.colWrite,
            this.colStop});
            this.dgvConnections.Location = new System.Drawing.Point(6, 19);
            this.dgvConnections.Name = "dgvConnections";
            this.dgvConnections.ReadOnly = true;
            this.dgvConnections.RowHeadersVisible = false;
            this.dgvConnections.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.dgvConnections.Size = new System.Drawing.Size(548, 135);
            this.dgvConnections.TabIndex = 0;
            this.dgvConnections.CellContentClick += new System.Windows.Forms.DataGridViewCellEventHandler(this.dgvConnections_CellContentClick);
            //
            // colType
            //
            this.colType.HeaderText = UiText.Translate("Type");
            this.colType.Name = "colType";
            this.colType.ReadOnly = true;
            this.colType.Width = 60;
            //
            // colDirection
            //
            this.colDirection.HeaderText = UiText.Translate("Direction");
            this.colDirection.Name = "colDirection";
            this.colDirection.ReadOnly = true;
            this.colDirection.Width = 70;
            //
            // colAddress
            //
            this.colAddress.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.Fill;
            this.colAddress.HeaderText = UiText.Translate("Address");
            this.colAddress.Name = "colAddress";
            this.colAddress.ReadOnly = true;
            //
            // colStatus
            //
            this.colStatus.HeaderText = UiText.Translate("Status");
            this.colStatus.Name = "colStatus";
            this.colStatus.ReadOnly = true;
            this.colStatus.Width = 80;
            //
            // colWrite
            //
            this.colWrite.HeaderText = UiText.Translate("Write");
            this.colWrite.Name = "colWrite";
            this.colWrite.ReadOnly = true;
            this.colWrite.Width = 45;
            //
            // colStop
            //
            this.colStop.HeaderText = UiText.Translate("Action");
            this.colStop.Name = "colStop";
            this.colStop.ReadOnly = true;
            this.colStop.Text = UiText.Translate("Stop");
            this.colStop.UseColumnTextForButtonValue = true;
            this.colStop.Width = 60;
            //
            // gbLog
            //
            this.gbLog.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
            | System.Windows.Forms.AnchorStyles.Left)
            | System.Windows.Forms.AnchorStyles.Right)));
            this.gbLog.Controls.Add(this.btnClear);
            this.gbLog.Controls.Add(this.txtLog);
            this.gbLog.Location = new System.Drawing.Point(12, 269);
            this.gbLog.Name = "gbLog";
            this.gbLog.Size = new System.Drawing.Size(560, 180);
            this.gbLog.TabIndex = 2;
            this.gbLog.TabStop = false;
            this.gbLog.Text = UiText.Translate("Output Log");
            //
            // btnClear
            //
            this.btnClear.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.btnClear.Location = new System.Drawing.Point(479, 151);
            this.btnClear.Name = "btnClear";
            this.btnClear.Size = new System.Drawing.Size(75, 23);
            this.btnClear.TabIndex = 1;
            this.btnClear.Text = UiText.Translate("Clear");
            this.btnClear.UseVisualStyleBackColor = true;
            this.btnClear.Click += new System.EventHandler(this.btnClear_Click);
            //
            // txtLog
            //
            this.txtLog.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
            | System.Windows.Forms.AnchorStyles.Left)
            | System.Windows.Forms.AnchorStyles.Right)));
            this.txtLog.Location = new System.Drawing.Point(6, 19);
            this.txtLog.Multiline = true;
            this.txtLog.Name = "txtLog";
            this.txtLog.ReadOnly = true;
            this.txtLog.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtLog.Size = new System.Drawing.Size(548, 126);
            this.txtLog.TabIndex = 0;
            //
            // SerialOutputPass
            //
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(584, 461);
            this.Controls.Add(this.gbLog);
            this.Controls.Add(this.gbConnections);
            this.Controls.Add(this.gbAddConnection);
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.MinimumSize = new System.Drawing.Size(500, 400);
            this.Name = "SerialOutputPass";
            this.Text = UiText.Translate("MAVLink Output");
            this.FormClosing += new System.Windows.Forms.FormClosingEventHandler(this.SerialOutputPass_FormClosing);
            this.Load += new System.EventHandler(this.SerialOutputPass_Load);
            this.gbAddConnection.ResumeLayout(false);
            this.tableLayoutPanel1.ResumeLayout(false);
            this.tableLayoutPanel1.PerformLayout();
            this.gbConnections.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dgvConnections)).EndInit();
            this.gbLog.ResumeLayout(false);
            this.gbLog.PerformLayout();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.GroupBox gbAddConnection;
        private System.Windows.Forms.TableLayoutPanel tableLayoutPanel1;
        private System.Windows.Forms.Label lblType;
        private System.Windows.Forms.ComboBox cmbType;
        private System.Windows.Forms.Label lblDirection;
        private System.Windows.Forms.ComboBox cmbDirection;
        private System.Windows.Forms.Label lblPort;
        private System.Windows.Forms.TextBox txtPort;
        private System.Windows.Forms.Label lblExtra;
        private System.Windows.Forms.TextBox txtExtra;
        private System.Windows.Forms.CheckBox chkWriteAccess;
        private MissionPlanner.Controls.MyButton btnAdd;
        private System.Windows.Forms.GroupBox gbConnections;
        private System.Windows.Forms.DataGridView dgvConnections;
        private System.Windows.Forms.GroupBox gbLog;
        private System.Windows.Forms.Button btnClear;
        private System.Windows.Forms.TextBox txtLog;
        private System.Windows.Forms.DataGridViewTextBoxColumn colType;
        private System.Windows.Forms.DataGridViewTextBoxColumn colDirection;
        private System.Windows.Forms.DataGridViewTextBoxColumn colAddress;
        private System.Windows.Forms.DataGridViewTextBoxColumn colStatus;
        private System.Windows.Forms.DataGridViewCheckBoxColumn colWrite;
        private System.Windows.Forms.DataGridViewButtonColumn colStop;
    }
}
