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
      <div className="report-data-header">
        <div>
          <span>Название</span>
          <strong>{report.title}</strong>
        </div>

        <div>
          <span>Тип</span>
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

      <h3>Содержимое отчёта</h3>

      <pre>{JSON.stringify(report.content, null, 2)}</pre>
    </div>
  );
}