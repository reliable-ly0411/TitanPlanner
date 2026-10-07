#!/usr/bin/env python3
"""Fail the release on known vulnerabilities, including transitive dependencies."""
import json
from pathlib import Path
import sys


def findings(report):
    result = set()
    for project in report.get('projects', []):
        for framework in project.get('frameworks', []):
            for kind in ('topLevelPackages', 'transitivePackages'):
                for package in framework.get(kind, []):
                    for vulnerability in package.get('vulnerabilities', []):
                        result.add((package['id'], package['resolvedVersion'], vulnerability['severity'], vulnerability['advisoryurl']))
    return sorted(result)


if __name__ == '__main__':
    report = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))
    errors = report.get('problems', [])
    if errors or not report.get('projects'):
        raise SystemExit('Dependency audit is incomplete: ' + str(errors))
    issues = findings(report)
    for issue in issues:
        print(' | '.join(issue))
    if issues:
        raise SystemExit(f'{len(issues)} vulnerable dependency/advisory pairs; release blocked')
    print('No known vulnerabilities in resolved application dependencies.')
