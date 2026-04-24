# uncnip-list

Generate IPv4 CIDR lists for CN IP ranges and non-CN IP ranges.

The generator reads CN route data from [misakaio/chnroutes2](https://github.com/misakaio/chnroutes2) and writes:

- `dist/cnip.txt`: CN IPv4 routes from `chnroutes2`.
- `dist/uncnip.txt`: IPv4 routes outside the CN list. Use this as the overseas CIDR list for iKuai policy routing.
- `dist/source.json`: Source hash and generated list counts.

## Generate locally

```bash
python scripts/generate_uncnip.py
```

## Upstream update

GitHub Actions runs `.github/workflows/generate-uncnip.yml` every hour, shortly after the upstream `chnroutes2` hourly update. It regenerates the files and commits only when the upstream data changes the generated output.

You can also run the workflow manually from the GitHub Actions tab.

## Data source

This project uses `chnroutes.txt` from `misakaio/chnroutes2`, which is generated from BGP feeds and updated hourly by that project.

`chnroutes2` data is licensed under CC-BY-SA. Check the upstream repository for the current license details.
