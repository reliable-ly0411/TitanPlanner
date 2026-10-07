using System;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using MissionPlanner.Utilities;

namespace MissionPlannerTests
{
    [TestClass]
    public class DownloadRegressionTests
    {
        private sealed class ResponseServer : IDisposable
        {
            private readonly TcpListener listener = new TcpListener(IPAddress.Loopback, 0);
            private readonly Task server;
            public readonly string Url;
            public ResponseServer(string response)
            {
                listener.Start();
                Url = "http://127.0.0.1:" + ((IPEndPoint)listener.LocalEndpoint).Port + "/test";
                server = Task.Run(() => {
                    using (var connection = listener.AcceptTcpClient())
                    using (var stream = connection.GetStream())
                    using (var reader = new StreamReader(stream, Encoding.ASCII, false, 1024, true))
                    {
                        stream.ReadTimeout = 10000;
                        while (!string.IsNullOrEmpty(reader.ReadLine())) { }
                        byte[] bytes = Encoding.UTF8.GetBytes(response);
                        stream.Write(bytes, 0, bytes.Length);
                    }
                });
            }
            public void Dispose() { listener.Stop(); Assert.IsTrue(server.Wait(10000), "HTTP fixture did not finish"); }
        }

        [TestMethod]
        public void ChunkedDownloadPreservesContent()
        {
            string path = Path.GetTempFileName();
            try
            {
                using (var server = new ResponseServer("HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\nConnection: close\r\n\r\n5\r\nhello\r\n0\r\n\r\n"))
                    Assert.IsTrue(Download.getFilefromNet(server.Url, path));
                Assert.AreEqual("hello", File.ReadAllText(path));
                Assert.IsFalse(File.Exists(path + ".new"));
            }
            finally { File.Delete(path); }
        }

        [TestMethod]
        public void TruncatedDownloadPreservesExistingFile()
        {
            string path = Path.GetTempFileName();
            File.WriteAllText(path, "keep existing file");
            try
            {
                using (var server = new ResponseServer("HTTP/1.1 200 OK\r\nContent-Length: 100\r\nConnection: close\r\n\r\nshort"))
                    Assert.IsFalse(Download.getFilefromNet(server.Url, path));
                Assert.AreEqual("keep existing file", File.ReadAllText(path));
                Assert.IsFalse(File.Exists(path + ".new"));
            }
            finally { File.Delete(path); File.Delete(path + ".new"); }
        }

        [TestMethod]
        public void FileSizeReadsHeadersWithoutDownloadingBody()
        {
            using (var server = new ResponseServer("HTTP/1.1 200 OK\r\nContent-Length: 5000000000\r\nConnection: close\r\n\r\n"))
                Assert.AreEqual(5000000000L, Download.GetFileSize(server.Url));
        }
    }
}
