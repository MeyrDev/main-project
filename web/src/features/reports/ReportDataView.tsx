import { ModelQualityReportView } from "./ModelQualityReportView";
import { PortfolioAnalyticsReportView } from "./PortfolioAnalyticsReportView";
import { ReportInfoCards } from "./ReportInfoCards";
import { RiskSummaryReportView } from "./RiskSummaryReportView";
import type { ReportData } from "./types";

type Props = {
  report: ReportData | null;
};

export function ReportDataView({ report }: Props) {
  if (!report) {
    return <p>Выберите отчёт из списка.</p>;
  }

  return (
    <div className="report-data">
      <ReportInfoCards report={report} />

      {report.report_type === "risk_summary" && (
        <RiskSummaryReportView content={report.content} />
      )}

      {report.report_type === "organization_card" && (
        <RiskSummaryReportView content={report.content} />
      )}

      {report.report_type === "portfolio_analytics" && (
        <PortfolioAnalyticsReportView content={report.content} />
      )}

      {report.report_type === "model_quality" && (
        <ModelQualityReportView content={report.content} />
      )}
    </div>
  );
}