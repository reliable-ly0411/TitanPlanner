using MissionPlanner.Comms;
using MissionPlanner.Utilities;
using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Windows.Forms;

namespace MissionPlanner.Controls
{
    public partial class SerialOutputPass : Form
    {
        // Track active connections with their listeners
        private List<ConnectionInfo> activeConnections = new List<ConnectionInfo>();

        private class ConnectionInfo
        {
            public string Type { get; set; }
            public string Direction { get; set; }
            public string Address { get; set; }
            public bool WriteAccess { get; set; }
            public MAVLinkInterface.Mirror Mirror { get; set; }
            public TcpListener Listener { get; set; }
            public int RowIndex { get; set; }
        }

        public SerialOutputPass()
        {
            InitializeComponent();

            MissionPlanner.Utilities.Tracking.AddPage(this.GetType().ToString(), this.Text);
        }

        private void SerialOutputPass_Load(object sender, EventArgs e)
        {
            // Set default selections
            cmbType.SelectedIndex = 0; // TCP
            cmbDirection.SelectedIndex = 1; // Outbound

            // Refresh the grid with any existing mirrors
            RefreshConnectionsList();

            Log("MAVLink Output ready");
        }

        private void cmbType_SelectedIndexChanged(object sender, EventArgs e)
        {
            UpdateUIForConnectionType();
        }

        private void cmbDirection_SelectedIndexChanged(object sender, EventArgs e)
        {
            UpdateUIForConnectionType();
        }

        private void UpdateUIForConnectionType()
        {
            string type = cmbType.SelectedItem?.ToString() ?? "TCP";
            string direction = cmbDirection.SelectedItem?.ToString() ?? "Outbound";

            switch (type)
            {
                case "Serial":
                    lblDirection.Visible = false;
                    cmbDirection.Visible = false;
                    lblPort.Text = UiText.Translate("COM Port:");
                    txtPort.Text = "";
                    lblExtra.Text = UiText.Translate("Baud Rate:");
                    txtExtra.Text = "115200";
                    break;

                case "TCP":
                case "UDP":
                    lblDirection.Visible = true;
                    cmbDirection.Visible = true;

                    if (direction == "Inbound")
                    {
                        lblPort.Text = UiText.Translate("Listen Port:");
                        txtPort.Text = "14550";
                        lblExtra.Text = "";
                        txtExtra.Text = "";
                        txtExtra.Visible = false;
                        lblExtra.Visible = false;
                    }
                    else // Outbound
                    {
                        lblPort.Text = UiText.Translate("Port:");
                        txtPort.Text = "14550";
                        lblExtra.Text = UiText.Translate("Host:");
                        txtExtra.Text = "127.0.0.1";
                        txtExtra.Visible = true;
                        lblExtra.Visible = true;
                    }
                    break;
            }
        }

        private void btnAdd_Click(object sender, EventArgs e)
        {
            try
            {
                string type = cmbType.SelectedItem?.ToString();
                string direction = cmbDirection.SelectedItem?.ToString() ?? "-";
                bool writeAccess = chkWriteAccess.Checked;

                if (string.IsNullOrEmpty(type))
                {
                    CustomMessageBox.Show(UiText.Translate("Please select a connection type."));
                    return;
                }

                MAVLinkInterface.Mirror mirror = new MAVLinkInterface.Mirror();
                mirror.MirrorStreamWrite = writeAccess;
                string address = "";
                TcpListener listener = null;

                switch (type)
                {
                    case "TCP":
                        if (direction == "Inbound")
                        {
                            int port;
                            if (!int.TryParse(txtPort.Text, out port))
                            {
                                CustomMessageBox.Show(UiText.Translate("Invalid port number."));
                                return;
                            }

                            mirror.MirrorStream = new TcpSerial();
                            listener = new TcpListener(IPAddress.Any, port);
                            listener.Start(0);
                            listener.BeginAcceptTcpClient(DoAcceptTcpClientCallback, (listener, mirror));

                            address = $":{port}";
                            Log($"TCP listener started on port {port}");
                        }
                        else // Outbound
                        {
                            string host = txtExtra.Text.Trim();
                            string port = txtPort.Text.Trim();

                            if (string.IsNullOrEmpty(host) || string.IsNullOrEmpty(port))
                            {
                                CustomMessageBox.Show(UiText.Translate("Please enter host and port."));
                                return;
                            }

                            mirror.MirrorStream = new TcpSerial()
                            {
                                retrys = 999999,
                                autoReconnect = true,
                                Host = host,
                                Port = port,
                                ConfigRef = "SerialOutputPassTCP"
                            };
                            mirror.MirrorStream.Open();

                            address = $"{host}:{port}";
                            Log($"TCP connection established to {address}");
                        }
                        break;

                    case "UDP":
                        if (direction == "Inbound")
                        {
                            int port;
                            if (!int.TryParse(txtPort.Text, out port))
                            {
                                CustomMessageBox.Show(UiText.Translate("Invalid port number."));
                                return;
                            }

                            var udp = new UdpSerial()
                            {
                                ConfigRef = "SerialOutputPassUDP",
                                Port = port.ToString()
                            };
                            udp.client = new UdpClient(port);
                            udp.IsOpen = true;
                            mirror.MirrorStream = udp;

                            address = $":{port}";
                            Log($"UDP listener started on port {port}");
                        }
                        else // Outbound
                        {
                            string host = txtExtra.Text.Trim();
                            int port;
                            if (!int.TryParse(txtPort.Text, out port) || string.IsNullOrEmpty(host))
                            {
                                CustomMessageBox.Show(UiText.Translate("Please enter valid host and port."));
                                return;
                            }

                            var udp = new UdpSerialConnect()
                            {
                                ConfigRef = "SerialOutputPassUDPCL"
                            };
                            udp.hostEndPoint = new IPEndPoint(IPAddress.Parse(host), port);
                            udp.client = new UdpClient();
                            udp.IsOpen = true;
                            mirror.MirrorStream = udp;

                            address = $"{host}:{port}";
                            Log($"UDP connection established to {address}");
                        }
                        break;

                    case "Serial":
                        string comPort = txtPort.Text.Trim();
                        int baudRate;
                        if (!int.TryParse(txtExtra.Text, out baudRate))
                        {
                            CustomMessageBox.Show(UiText.Translate("Invalid baud rate."));
                            return;
                        }

                        if (string.IsNullOrEmpty(comPort))
                        {
                            CustomMessageBox.Show(UiText.Translate("Please enter a COM port name."));
                            return;
                        }

                        mirror.MirrorStream = new SerialPort();
                        mirror.MirrorStream.PortName = comPort;
                        mirror.MirrorStream.BaudRate = baudRate;
                        mirror.MirrorStream.Open();
                        direction = "-";

                        address = $"{comPort}@{baudRate}";
                        Log($"Serial port {address} opened");
                        break;

                    default:
                        CustomMessageBox.Show(UiText.Translate("Unknown connection type."));
                        return;
                }

                // Add to MainV2 mirrors list
                MainV2.comPort.Mirrors.Add(mirror);

                // Add to our tracking list
                var connInfo = new ConnectionInfo
                {
                    Type = type,
                    Direction = direction,
                    Address = address,
                    WriteAccess = writeAccess,
                    Mirror = mirror,
                    Listener = listener
                };

                // Add row to grid
                int rowIndex = dgvConnections.Rows.Add(
                    type,
                    direction,
                    address,
                    "Connected",
                    writeAccess
                );
                connInfo.RowIndex = rowIndex;
                dgvConnections.Rows[rowIndex].Tag = connInfo;

                activeConnections.Add(connInfo);
            }
            catch (Exception ex)
            {
                Log($"Error: {ex.Message}");
                CustomMessageBox.Show(UiText.Format($"Failed to create connection: {ex.Message}"));
            }
        }

        private void DoAcceptTcpClientCallback(IAsyncResult ar)
        {
            try
            {
                var state = (ValueTuple<TcpListener, MAVLinkInterface.Mirror>)ar.AsyncState;
                TcpListener listener = state.Item1;
                MAVLinkInterface.Mirror mirror = state.Item2;

                TcpClient client = listener.EndAcceptTcpClient(ar);

                ((TcpSerial)mirror.MirrorStream).client = client;

                // Log on UI thread
                if (!IsDisposed && IsHandleCreated)
                {
                    BeginInvoke((Action)(() =>
                    {
                        Log($"TCP client connected from {client.Client.RemoteEndPoint}");
                    }));
                }

                // Continue accepting more clients
                listener.BeginAcceptTcpClient(DoAcceptTcpClientCallback, state);
            }
            catch (ObjectDisposedException)
            {
                // Listener was stopped, ignore
            }
            catch (Exception ex)
            {
                if (!IsDisposed && IsHandleCreated)
                {
                    BeginInvoke((Action)(() =>
                    {
                        Log($"TCP accept error: {ex.Message}");
                    }));
                }
            }
        }

        private void dgvConnections_CellContentClick(object sender, DataGridViewCellEventArgs e)
        {
            // Check if Stop button was clicked
            if (e.ColumnIndex == colStop.Index && e.RowIndex >= 0)
            {
                StopConnection(e.RowIndex);
            }
        }

        private void StopConnection(int rowIndex)
        {
            try
            {
                var row = dgvConnections.Rows[rowIndex];
                var connInfo = row.Tag as ConnectionInfo;

                if (connInfo != null)
                {
                    // Stop listener if exists
                    if (connInfo.Listener != null)
                    {
                        connInfo.Listener.Stop();
                        connInfo.Listener = null;
                    }

                    // Close stream
                    if (connInfo.Mirror?.MirrorStream != null)
                    {
                        try
                        {
                            connInfo.Mirror.MirrorStream.Close();
                        }
                        catch { }
                    }

                    // Remove from MainV2 mirrors
                    if (connInfo.Mirror != null)
                    {
                        MainV2.comPort.Mirrors.Remove(connInfo.Mirror);
                    }

                    activeConnections.Remove(connInfo);

                    Log($"Stopped {connInfo.Type} connection to {connInfo.Address}");
                }

                // Remove row from grid
                dgvConnections.Rows.RemoveAt(rowIndex);

                // Update row indices for remaining connections
                for (int i = 0; i < dgvConnections.Rows.Count; i++)
                {
                    var info = dgvConnections.Rows[i].Tag as ConnectionInfo;
                    if (info != null)
                    {
                        info.RowIndex = i;
                    }
                }
            }
            catch (Exception ex)
            {
                Log($"Error stopping connection: {ex.Message}");
            }
        }

        private void RefreshConnectionsList()
        {
            // Show any existing mirrors from MainV2.comPort.Mirrors
            foreach (var mirror in MainV2.comPort.Mirrors)
            {
                if (mirror.MirrorStream != null)
                {
                    string type = "Unknown";
                    string direction = "-";
                    string address = "";

                    if (mirror.MirrorStream is TcpSerial)
                    {
                        type = "TCP";
                        var tcp = mirror.MirrorStream as TcpSerial;
                        address = $"{tcp.Host}:{tcp.Port}";
                        direction = string.IsNullOrEmpty(tcp.Host) ? "Inbound" : "Outbound";
                    }
                    else if (mirror.MirrorStream is UdpSerial)
                    {
                        type = "UDP";
                        direction = "Inbound";
                        var udp = mirror.MirrorStream as UdpSerial;
                        address = $":{udp.Port}";
                    }
                    else if (mirror.MirrorStream is UdpSerialConnect)
                    {
                        type = "UDP";
                        direction = "Outbound";
                        var udp = mirror.MirrorStream as UdpSerialConnect;
                        address = udp.hostEndPoint?.ToString() ?? "";
                    }
                    else if (mirror.MirrorStream is SerialPort)
                    {
                        type = "Serial";
                        var serial = mirror.MirrorStream as SerialPort;
                        address = $"{serial.PortName}@{serial.BaudRate}";
                    }

                    string status = mirror.MirrorStream.IsOpen ? "Connected" : "Disconnected";

                    int rowIndex = dgvConnections.Rows.Add(
                        type,
                        direction,
                        address,
                        status,
                        mirror.MirrorStreamWrite
                    );

                    var connInfo = new ConnectionInfo
                    {
                        Type = type,
                        Direction = direction,
                        Address = address,
                        WriteAccess = mirror.MirrorStreamWrite,
                        Mirror = mirror,
                        RowIndex = rowIndex
                    };
                    dgvConnections.Rows[rowIndex].Tag = connInfo;
                    activeConnections.Add(connInfo);
                }
            }
        }

        private void Log(string message)
        {
            if (InvokeRequired)
            {
                BeginInvoke((Action)(() => Log(message)));
                return;
            }

            txtLog.AppendText($"[{DateTime.Now:HH:mm:ss}] {message}\r\n");
        }

        private void btnClear_Click(object sender, EventArgs e)
        {
            txtLog.Clear();
        }

        private void SerialOutputPass_FormClosing(object sender, FormClosingEventArgs e)
        {
            // Note: We don't stop connections on form close
            // They should continue running in the background
            // User can reopen the form to see/manage them
        }
    }
}
