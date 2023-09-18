using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;
using AGI.Attr;
using AGI.Hpop.Plugin;
using AGI.Plugin;
using AGI.STK.Plugin;
using AGI.STKObjects;

namespace Python.Density.HPOP
{
    [Guid("E6E94E61-4CD9-4E2C-ACB9-FE68B8694B81")]
    [ProgId("Python.Density.HPOP")]
    [ClassInterface(ClassInterfaceType.None)]
    public class DensityPlugin : IAgAsDensityModelPlugin, IAgUtPluginConfig
    {
        private bool _DebugMode = false;
        private object _oPluginConfig = null;
        private IAgUtPluginSite _AgUtPluginSite = null;
        private AgStkPluginSite _AgStkPluginSite = null;
        private AgStkObjectRoot _AgStkObjectRoot = null;
        private string m_scenario_start = null;
        private string m_scenario_stop = null;
        private AgScenario m_scenario = null;

        #region IAgAsDensityModelPlugin Implementation
        public void Register(AgAsDensityModelResultRegister Result)
        {
            if (_DebugMode)
            {
                Result.Message(AgEUtLogMsgType.eUtLogMsgDebug, "DensityExponentialExample:Register()");
            }
        }

        public bool Init(IAgUtPluginSite Site)
        {
            if (_DebugMode)
            {
                MessageViewerLog(AgEUtLogMsgType.eUtLogMsgDebug, "DensityExponentialExample:Init()");
            }
            if (Site != null)
            {
                _AgUtPluginSite = Site;
                _AgStkPluginSite = (AgStkPluginSite)Site;
                _AgStkObjectRoot = _AgStkPluginSite.StkRootObject;

                _AgStkObjectRoot.UnitPreferences.SetCurrentUnit("DateFormat", "ISO-YMD");
                m_scenario = (AgScenario)_AgStkObjectRoot.CurrentScenario;
            }
            return true;

        }

        public void Free()
        {
            if (_DebugMode)
            {
                MessageViewerLog(AgEUtLogMsgType.eUtLogMsgDebug, "DensityExponentialExample:Free()");
            }

            _AgUtPluginSite = null;
        }

        public bool Evaluate(AgAsDensityModelResultEval ResultEval)
        {
            CallPythonScript(ResultEval);
            return true;
        }

        public string CentralBody()
        {
            return "Earth";
        }

        public bool ComputesTemperature()
        {
            return false;
        }

        public bool ComputesPressure()
        {
            return false;
        }

        public bool UsesAugmentedSpaceWeather()
        {
            return true;
        }

        public void AtmFluxLags(ref double F10p7Lag, ref double F10p7MeanLag, ref double GeoFluxLag)
        {
            
        }

        public void AugmentedAtmFluxLags(ref double M10p7Lag, ref double M10p7MeanLag, ref double S10p7Lag, ref double S10p7MeanLag, ref double Y10p7Lag, ref double Y10p7MeanLag, ref double DstDTcLag)
        {
            
        }

        public double GetLowestValidAltitude()
        {
            return 90.0 * 1000.0;
        }
        #endregion IAgAsDensityModelPlugin Implementation

        #region IAgUtPluginConfig Implementation 
        public object GetPluginConfig(AgAttrBuilder pAttrBuilder)
        {

            return _oPluginConfig;
        }

        public void VerifyPluginConfig(AgUtPluginConfigVerifyResult pPluginCfgResult)
        {
            MessageViewerLog(AgEUtLogMsgType.eUtLogMsgDebug, "DensityExponentialExample:VerifyPluginConfig()");

            pPluginCfgResult.Result = true;
            pPluginCfgResult.Message = "OK";
        }
        #endregion IAgUtPluginConfig Implementation
        public void CallPythonScript(AgAsDensityModelResultEval ResultEval)
        {

            var date_epmin = ResultEval.DateString("EpMin");

            var latRad = 0.0; var lonRad = 0.0; var altM = 0.0;
            ResultEval.LatLonAlt(ref latRad, ref lonRad, ref altM);
            var lat = latRad * 180.0 / Math.PI;
            var lon = (lonRad * 180.0 / Math.PI) + 180;
            var alt = altM / 1000.0;

            m_scenario_start = m_scenario.StartTime.ToString();
            m_scenario_stop = m_scenario.StopTime.ToString();

            var pythonPath = @"C:\Users\sasrivas\myEnv\Scripts\pythonw.exe";
            var pathToScript = @"C:\Users\sasrivas\OneDrive - ANSYS, Inc\Work\12_R&D\ACE SME Mentoring Program\SpaceWeather x Astro\code\plugin_v2_1\ReadWAMIPEdata_v2_1.py";

            var density = 0.0;
            var cmd = $"{pathToScript} {date_epmin} {alt} {lat} {lon} {m_scenario_start} {m_scenario_stop}";
            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = pythonPath;
            start.Arguments = cmd;
            start.UseShellExecute = false;
            start.RedirectStandardOutput = true;
            using(Process process = Process.Start(start))
            {
                using(StreamReader reader = process.StandardOutput)
                {
                    density = Double.Parse(reader.ReadToEnd());
                    //MessageViewerLog(AgEUtLogMsgType.eUtLogMsgDebug, density.ToString());
                }
            }
            ResultEval.SetDensity(density);
        }

        private void MessageViewerLog(AgEUtLogMsgType messageType, string message)
        {
            if (_AgUtPluginSite != null)
            {
                _AgUtPluginSite.Message(messageType, message);
            }
        }
    }
}
