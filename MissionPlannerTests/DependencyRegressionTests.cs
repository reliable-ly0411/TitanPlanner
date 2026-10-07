using System;
using System.IO;
using Ionic.Zip;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using SkiaSharp;

namespace MissionPlannerTests
{
    [TestClass]
    public class DependencyRegressionTests
    {
        [TestMethod]
        public void ZipRoundTripPreservesChineseNamesAndContent()
        {
            using (var stream = new MemoryStream())
            {
                using (var zip = new ZipFile(System.Text.Encoding.UTF8))
                {
                    zip.AddEntry("测试/航线.txt", "航点 1：12.345", System.Text.Encoding.UTF8);
                    zip.Save(stream);
                }
                stream.Position = 0;
                using (var zip = ZipFile.Read(stream))
                using (var content = new MemoryStream())
                {
                    zip["测试/航线.txt"].Extract(content);
                    StringAssert.Contains(System.Text.Encoding.UTF8.GetString(content.ToArray()), "航点 1：12.345");
                }
            }
        }

        [TestMethod]
        public void ZipExtractionCannotEscapeDestination()
        {
            var root = Path.Combine(Path.GetTempPath(), "TitanPlanner-zip-" + Guid.NewGuid());
            Directory.CreateDirectory(Path.Combine(root, "destination"));
            try
            {
                using (var stream = new MemoryStream())
                {
                    using (var zip = new ZipFile())
                    {
                        zip.AddEntry("../outside.txt", "must stay inside destination");
                        zip.Save(stream);
                    }
                    stream.Position = 0;
                    using (var zip = ZipFile.Read(stream))
                    {
                        try { zip.ExtractAll(Path.Combine(root, "destination")); }
                        catch (ZipException) { }
                        catch (ArgumentException) { }
                    }
                }
                Assert.IsFalse(File.Exists(Path.Combine(root, "outside.txt")));
            }
            finally { Directory.Delete(root, true); }
        }

        [TestMethod]
        public void SkiaManagedAndNativeLibrariesRenderTogether()
        {
            using (var bitmap = new SKBitmap(8, 8))
            {
                bitmap.Erase(SKColors.Red);
                Assert.AreEqual(SKColors.Red, bitmap.GetPixel(4, 4));
                using (var image = SKImage.FromBitmap(bitmap))
                using (var png = image.Encode(SKEncodedImageFormat.Png, 100))
                    Assert.IsTrue(png.Size > 0);
            }
        }
    }
}
