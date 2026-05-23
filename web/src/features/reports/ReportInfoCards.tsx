import type { ReportData } from "./types";

type Props = {
  report: ReportData;
};

export function ReportInfoCards({ report }: Props) {
  return (
    <div className="report-info-grid">
      <div>
        <span>Название</span>
        <strong>{report.title}</strong>
      </div>

      <div>
        <span>Тип отчёта</span>
        <strong>{report.report_type}</strong>
      </div>

      <div>
        <span>Статус</span>
        <strong>{report.status}</strong>
      </div>

      <div>
        <span>Сформирован</span>
        <strong>{new Date(report.generated_at).toLocaleString()}</strong>
      </div>
    </div>
  );
}