# Hold off on prophet image generation, probably not useful since I buy small caps

import sys 
import argparse as ap
import pathlib
from jinja2 import Template
from datetime import date
from stocks.util import get_config
from stocks.report import make_risk_metrics, make_performance_plot

def main(args):
    with open(args.template) as file_:
      template = Template(file_.read())
    end_date = str(date.today())

    options = dict(Version="1.0.0", CurrDate=end_date)
    # Get config
    cfg = get_config()
    for report_cfg in cfg["reports"]:
        stocks = report_cfg["stocks"]
        weights = report_cfg["weights"]
        start_date = report_cfg["start_date"]
        report_name = report_cfg["name"]
        if isinstance(weights, str):
            # set equal list based on stock length
            # TODO add more types later
            weights = [1.00 / len(stocks)] * len(stocks)
            risk_metrics = make_risk_metrics(stocks, weights, start_date, end_date)
        # Add Var, VaR, CVaR, CDaR
        options["RISK_METRICS"] = risk_metrics

        # Relative paths to performance images,
        # images are in the same directory as index.html
        output_folder = f"{args.output}/{report_name}"
        performance_images = []
        image_name = f"{start_date}_{end_date}_basic.png"
        plot_made = make_performance_plot(
            stocks,
            start_date=start_date,
            end_date=end_date,
            file_name=f"{output_folder}/${image_name}"
        )
        if plot_made is not None:
            performance_images.append(image_name)
        options["PERFORMANCE_IMAGES"] = performance_images
        renderer_template = template.render(**options)
        # Make folder even if exists
        pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True) 
        with open(f"{output_folder}/index.html", "w", errors='ignore') as f:
            f.write(renderer_template)

    
if __name__ == "__main__":
    assert sys.version_info >= (3, 6)
    parser = ap.ArgumentParser()
    parser.add_argument("-o",
                        "--output",
                        help="Output folder",
                        default="report")
    parser.add_argument("-t", 
                        "--template", 
                        help="Template file", 
                        default="stocks/template.jinja2") 
    args = parser.parse_args()
    main(args)