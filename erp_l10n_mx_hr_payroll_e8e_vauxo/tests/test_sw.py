import requests

import string
import random


def _l10n_mx_edi_sw_info(service_type):
  test = True
  username = 'opendsf@gmail.com'
  password = '123456789'
  url = ('http://services.test.sw.com.mx/'
         if test else 'https://services.sw.com.mx/')
  url_service = url + ('cfdi33/stamp/v3/b64' if service_type == 'sign'
                       else 'cfdi33/cancel/csd')
  url_login = url + 'security/authenticate'
  return {
    'url': url_service,
    'multi': False,  # TODO: implement multi
    'username': username,
    'password': password,
    'login_url': url_login,
  }

def _l10n_mx_edi_sw_token(pac_info):
  """Get token for SW PAC
  return: string token, string error.
    e.g. if token is success
         (token, None)
    e.g. if token is not success
         (None, error)
  """
  if pac_info['password'] and not pac_info['username']:
    # token is configured directly instead of user/password
    token = pac_info['password'].strip()
    return token, None
  try:
    headers = {
      'user': pac_info['username'],
      'password': pac_info['password'],
      'Cache-Control': "no-cache"
    }
    response = requests.post(pac_info['login_url'], headers=headers)
    response.raise_for_status()
    response_json = response.json()
    return response_json['data']['token'], None
  except (requests.exceptions.RequestException, KeyError, TypeError) as req_e:
    return None, str(req_e)


pac_info = _l10n_mx_edi_sw_info('sign')
print ("Informacion del pac ", pac_info)
token = _l10n_mx_edi_sw_token(pac_info)

print ("Token ", token)


url = "https://services.sw.com.mx/cfdi33/stamp/v3/b64"

payload="--gqV6xYBinbokqRJGrxZN0PTDY7IsqZ\nContent-Type: text/xml\nContent-Transfer-Encoding: binary\nContent-Disposition: form-data; name=\"xml\"; filename=\"xml\"\n\nPD94bWwgdmVyc2lvbj0nMS4wJyBlbmNvZGluZz0nVVRGLTgnPz4KPGNmZGk6Q29tcHJvYmFudGUg\neG1sbnM6Y2ZkaT0iaHR0cDovL3d3dy5zYXQuZ29iLm14L2NmZC8zIiB4bWxuczp4c2k9Imh0dHA6\nLy93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIiBWZXJzaW9uPSIzLjMiIFNlbGxv\nPSJkYUZCTXBlNzM0MFRUYlpEVkJLek45akNvNU5RVWtKNGFBNW0xZ1JWYktrajJuN2dQcUNjcldR\ndkIzTUp5VHZMQjZ0MjNpNXVyTzkwWWtabGFSS1o5Um90Q1c1S0RPZTFJZy9URG04eVhYQW9hVC80\nU0NDK0FWSkFuSkZ6ZmtlYkFGSzFKamRSTER3QjdCbnFncGtPeVNCdlJoVVMwY2pjbUtoSS9hcE9S\neWtYNm55MTJkWjRaRmhTT2Njb05hTlc2cExWcEp1ZGJXRFJMaFIxRWl3Qk5ndEoxYURhOVkzUzVa\nQ0E0WTJjVHUyVnI2b1h5cENVTVduUWhJTGlkTjFWczBSS3NJMXhURUJicnJWYzFBMWh3NGN3VUFY\nU3E2bmY4THJIMzFQSG1Ccjg1dzFsZnAvdmpkMnVONXo1WGdwWTNwdTd4Z1BnOTh2Y1g0Uks2a2J1\nQmc9PSIgeHNpOnNjaGVtYUxvY2F0aW9uPSJodHRwOi8vd3d3LnNhdC5nb2IubXgvY2ZkLzMgaHR0\ncDovL3d3dy5zYXQuZ29iLm14L3NpdGlvX2ludGVybmV0L2NmZC8zL2NmZHYzMy54c2QiIEZlY2hh\nPSIyMDIxLTAyLTE0VDEwOjE1OjExIiBGb3JtYVBhZ289Ijk5IiBOb0NlcnRpZmljYWRvPSIzMDAw\nMTAwMDAwMDQwMDAwMjQzNCIgQ2VydGlmaWNhZG89Ik1JSUZ1ekNDQTZPZ0F3SUJBZ0lVTXpBd01E\nRXdNREF3TURBME1EQXdNREkwTXpRd0RRWUpLb1pJaHZjTkFRRUxCUUF3Z2dFck1ROHdEUVlEVlFR\nRERBWkJReUJWUVZReExqQXNCZ05WQkFvTUpWTkZVbFpKUTBsUElFUkZJRUZFVFVsT1NWTlVVa0ZE\nU1U5T0lGUlNTVUpWVkVGU1NVRXhHakFZQmdOVkJBc01FVk5CVkMxSlJWTWdRWFYwYUc5eWFYUjVN\nU2d3SmdZSktvWklodmNOQVFrQkZobHZjMk5oY2k1dFlYSjBhVzVsZWtCellYUXVaMjlpTG0xNE1S\nMHdHd1lEVlFRSkRCUXpjbUVnWTJWeWNtRmtZU0JrWlNCallXUnBlakVPTUF3R0ExVUVFUXdGTURZ\nek56QXhDekFKQmdOVkJBWVRBazFZTVJrd0Z3WURWUVFJREJCRFNWVkVRVVFnUkVVZ1RVVllTVU5Q\nTVJFd0R3WURWUVFIREFoRFQxbFBRVU5CVGpFUk1BOEdBMVVFTFJNSU1pNDFMalF1TkRVeEpUQWpC\nZ2txaGtpRzl3MEJDUUlURm5KbGMzQnZibk5oWW14bE9pQkJRMFJOUVMxVFFWUXdIaGNOTVRrd05q\nRTNNVGswTkRFMFdoY05Nak13TmpFM01UazBOREUwV2pDQjRqRW5NQ1VHQTFVRUF4TWVSVk5EVlVW\nTVFTQkxSVTFRUlZJZ1ZWSkhRVlJGSUZOQklFUkZJRU5XTVNjd0pRWURWUVFwRXg1RlUwTlZSVXhC\nSUV0RlRWQkZVaUJWVWtkQlZFVWdVMEVnUkVVZ1ExWXhKekFsQmdOVkJBb1RIa1ZUUTFWRlRFRWdT\nMFZOVUVWU0lGVlNSMEZVUlNCVFFTQkVSU0JEVmpFbE1DTUdBMVVFTFJNY1JVdFZPVEF3TXpFM00w\nTTVJQzhnV0VsUlFqZzVNVEV4TmxGRk5ERWVNQndHQTFVRUJSTVZJQzhnV0VsUlFqZzVNVEV4Tmsx\nSFVrMWFVakExTVI0d0hBWURWUVFMRXhWRmMyTjFaV3hoSUV0bGJYQmxjaUJWY21kaGRHVXdnZ0Vp\nTUEwR0NTcUdTSWIzRFFFQkFRVUFBNElCRHdBd2dnRUtBb0lCQVFDTjBwZUtwZ2ZPTDc1aVlSdjFm\ncXErb1ZZc0xQVlVSL0dpYlltR0tjOUluSEZ5NWxZRjZPVFlqbklJdm1rT2RSb2JiR2xDVXhPUlgv\ndExzbDhZYTlnbTZZbzdoSG5PRFJCSUR1cDNHSVNGekIvOTZSOUsvTXpZUU9jc2NNSW9CREFSYXlj\nbkx2eTdGbE12TzcvcmxWbnNTQVJ4WlJPOEt6OFpra3NqMnpwZVlwalpJeWEvMzY5K29HcVFrMWNU\nUmtIbzU5SnZKNFRmYmsvM2lJeWY0SC9Jbmk5bkJlOWNZV28wTW5Lb2I3RER0L3ZzZGk1dEE4bU10\nQTk1M0xhcE55Q1pJRENSUVFsVUdOZ0RxWTkvOEY1bVV2VmdrY2N6c0lnR2R2Zjl2TVFQU2YzampD\naUtqN2o2dWN4bDErRndKV21idmdObWlhVVIvMHE0bTJybTc4bEZBZ01CQUFHakhUQWJNQXdHQTFV\nZEV3RUIvd1FDTUFBd0N3WURWUjBQQkFRREFnYkFNQTBHQ1NxR1NJYjNEUUVCQ3dVQUE0SUNBUUJj\ncGoxVGpUNGppaW5JdWpJZEFsRnpFNmtSd1lKQ25ERzA4elNwNGtTblNoanhBREdFWEgyY2hlaEtN\nVjBGWTdjNG5qQTVlREdkQS9HMk9DVFB2RjVycGVDWlA1RHc1MDRSWmtZRGwyc3VSeit3YTFzTkJW\ncGJuQkpFSzBmUWNOM0lmdEJ3c2dORmRGaFV0Q3l3M2x1czFTU0piUHhqTEhTNkZjWlo1MVlTZUlm\nY05YT0F1VHFkaW11c2FYcTE1R3JTckNPa002bjJqZmoyc01KWU0ySFhhWEo2ckdURWdZbWhZZHd4\nV3RpbDZSZlpCK2ZHUS9IOUk5V0xubDRLVFpVUzZDOStOTEhoNEZQRGhTazE5ZnBTMlMvNTZhcWdG\nb0dBa1hBWXQ5Rnk1RUNhUGNVTElmSjFERWJzWEt5UmRDdjNKWTg5KzBNTmtPZGFEbnNlbVMybzVH\nbDA4ekk0aVl0dDNMNDBnQVo2ME5QaDMxa1ZMbllOc212Zk54WXlLcCtBZUp0REh5Vzl3N2Z0TTBI\nb2krQnVSbWNBUVNLRlYzcGs4ajUxbGEranJSQnJBVXY4YmxiUmNRNUJpWlV3SnpIRkVLSXdUc1JH\nb1J5RXg5NnNObkIwM242R1R3aklHejkyU21MZE5sOTVyOXJrdnArMm00UzZxMWxQdVhhRmc3REdC\nclhXQzhpeXFlV0UyaW9iZHdJSXVYUFRNVnFRYjEybTFkQWtKVlJPNU5kSG5QL01wcU92T2dMcW9a\nQk5IR3lCZzRHcW00c0NKSEN4QTFjOEVsZmEyUlFUQ2swdEF6bGxMNHZPbkkxR0hrR0puNjV4b2tH\nc2FVNEI0RDM2eGg3ZVdyZmo0L3BnV0htdG9EQVlhOHd6U3dvMkdWQ1pPcyttdEVnT1FCOTEvZz09\nIiBTdWJUb3RhbD0iMS4wMCIgTW9uZWRhPSJNWE4iIFRvdGFsPSIxLjE2IiBUaXBvRGVDb21wcm9i\nYW50ZT0iSSIgTWV0b2RvUGFnbz0iUFVFIiBMdWdhckV4cGVkaWNpb249IjQ0NTkwIj4KICA8Y2Zk\naTpFbWlzb3IgUmZjPSJFS1U5MDAzMTczQzkiIE5vbWJyZT0iTXkgQ29tcGFueSIgUmVnaW1lbkZp\nc2NhbD0iNjAxIi8+CiAgPGNmZGk6UmVjZXB0b3IgUmZjPSJYQVhYMDEwMTAxMDAwIiBOb21icmU9\nIlRFU1QiIFVzb0NGREk9IlAwMSIvPgogIDxjZmRpOkNvbmNlcHRvcz4KICAgIDxjZmRpOkNvbmNl\ncHRvIENsYXZlUHJvZFNlcnY9IjAxMDEwMTAxIiBDYW50aWRhZD0iMS4wIiBDbGF2ZVVuaWRhZD0i\nSDg3IiBVbmlkYWQ9IlVuaXQocykiIERlc2NyaXBjaW9uPSJ0ZXN0IiBWYWxvclVuaXRhcmlvPSIx\nLjAwIiBJbXBvcnRlPSIxLjAwIj4KICAgICAgPGNmZGk6SW1wdWVzdG9zPgogICAgICAgIDxjZmRp\nOlRyYXNsYWRvcz4KICAgICAgICAgIDxjZmRpOlRyYXNsYWRvIEJhc2U9IjEuMDAiIEltcHVlc3Rv\nPSIwMDIiIFRpcG9GYWN0b3I9IlRhc2EiIFRhc2FPQ3VvdGE9IjAuMTYwMDAwIiBJbXBvcnRlPSIw\nLjE2Ii8+CiAgICAgICAgPC9jZmRpOlRyYXNsYWRvcz4KICAgICAgPC9jZmRpOkltcHVlc3Rvcz4K\nICAgIDwvY2ZkaTpDb25jZXB0bz4KICA8L2NmZGk6Q29uY2VwdG9zPgogIDxjZmRpOkltcHVlc3Rv\ncyBUb3RhbEltcHVlc3Rvc1RyYXNsYWRhZG9zPSIwLjE2Ij4KICAgIDxjZmRpOlRyYXNsYWRvcz4K\nICAgICAgPGNmZGk6VHJhc2xhZG8gSW1wb3J0ZT0iMC4xNiIgSW1wdWVzdG89IjAwMiIgVGlwb0Zh\nY3Rvcj0iVGFzYSIgVGFzYU9DdW90YT0iMC4xNjAwMDAiLz4KICAgIDwvY2ZkaTpUcmFzbGFkb3M+\nCiAgPC9jZmRpOkltcHVlc3Rvcz4KPC9jZmRpOkNvbXByb2JhbnRlPgo=\n\n--gqV6xYBinbokqRJGrxZN0PTDY7IsqZ--\n"
headers = {
  'Authorization': 'bearer T2lYQ0t4L0RHVkR4dHZ5Nkk1VHNEakZ3Y0J4Nk9GODZuRyt4cE1wVm5tbXB3YVZxTHdOdHAwVXY2NTdJb1hkREtXTzE3dk9pMmdMdkFDR2xFWFVPUTQyWFhnTUxGYjdKdG8xQTZWVjFrUDNiOTVrRkhiOGk3RHladHdMaEM0cS8rcklzaUhJOGozWjN0K2h6R3gwQzF0c0g5aGNBYUt6N2srR3VoMUw3amtvPQ.T2lYQ0t4L0RHVkR4dHZ5Nkk1VHNEakZ3Y0J4Nk9GODZuRyt4cE1wVm5tbFlVcU92YUJTZWlHU3pER1kySnlXRTF4alNUS0ZWcUlVS0NhelhqaXdnWTRncklVSWVvZlFZMWNyUjVxYUFxMWFxcStUL1IzdGpHRTJqdS9Zakw2UGRiMTFPRlV3a2kyOWI5WUZHWk85ODJtU0M2UlJEUkFTVXhYTDNKZVdhOXIySE1tUVlFdm1jN3kvRStBQlpLRi9NeWJrd0R3clhpYWJrVUMwV0Mwd3FhUXdpUFF5NW5PN3J5cklMb0FETHlxVFRtRW16UW5ZVjAwUjdCa2g0Yk1iTExCeXJkVDRhMGMxOUZ1YWlIUWRRVC8yalFTNUczZXdvWlF0cSt2UW0waFZKY2gyaW5jeElydXN3clNPUDNvU1J2dm9weHBTSlZYNU9aaGsvalpQMUxxQTR3QW5OQlBWdVE2bFdmSzVJWU5TdllBK2ZUTDlUN0RsOTFIdnE0L1d6MXo1SDgwczZ2ZXNXVzN6aFB1ODA5enlMb01JMFJ1QWwva1NmZU1qKzBGTUhQYk5USkFUOHc4VGtqcmZEUlRCL2ZFRXdGejFsK2Qxc1VyQWRVWHJzZFl5NzBWWE9nUVZGa2o2T0xYZGZnWGs9.ByQuDgtL5W-Sc-7PtppbOdvaP7un--mqlxz5VLQS9B0',
  'Content-Type': 'multipart/form-data; boundary="gqV6xYBinbokqRJGrxZN0PTDY7IsqZ"'
}

xml = """PD94bWwgdmVyc2lvbj0nMS4wJyBlbmNvZGluZz0nVVRGLTgnPz4KPGNmZGk6Q29tcHJvYmFudGUg
eG1sbnM6Y2ZkaT0iaHR0cDovL3d3dy5zYXQuZ29iLm14L2NmZC8zIiB4bWxuczp4c2k9Imh0dHA6
Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIiBWZXJzaW9uPSIzLjMiIFNlbGxv
PSJRTTJvS3NtYzdpTkNMU0VjelNYR0laRG1RM2tJMjZwUFVyUk9kUUhodjhlcFhGUHlKWW5WeldQ
elBTckZNeXcrZzBSVHhIUmY2amVGVmRKWTZuYW1iQUh3dDIvcnFCTmVmWUwwdmFGcThUV0tEZTdn
VFk0QThWQmxWQm1wR2dJSHNrLzNOeWFHRHFaVHI3bmxRemlXaXVLdHZGT2UwWis4REt1N1U5QTRH
Qi9ybU96VmJPdlhkQnZncTBTeTRGVTEzT0ZLcjgvRnpjT1lJUDVRbmYzSEhwNVhpeHdLcitEU2Ev
endyL0EzN2p1NzNhMHZVbnVUbjNITmRGM29vWGdkQ2daeHFKc2sxVFNPdXk3MXdoOThNWHNoY3NH
SlVjajd2U2IzZkFlUGhOcHJZbEF3dkxCVGo1WTNjOVlBN2FzK0VJS3JyNlFGbnhidDkrcXFVUW9v
aEE9PSIgeHNpOnNjaGVtYUxvY2F0aW9uPSJodHRwOi8vd3d3LnNhdC5nb2IubXgvY2ZkLzMgaHR0
cDovL3d3dy5zYXQuZ29iLm14L3NpdGlvX2ludGVybmV0L2NmZC8zL2NmZHYzMy54c2QiIEZlY2hh
PSIyMDIxLTAyLTIyVDExOjA0OjI5IiBGb3JtYVBhZ289Ijk5IiBOb0NlcnRpZmljYWRvPSIzMDAw
MTAwMDAwMDQwMDAwMjQxNyIgQ2VydGlmaWNhZG89Ik1JSUdCRENDQSt5Z0F3SUJBZ0lVTXpBd01E
RXdNREF3TURBME1EQXdNREkwTVRjd0RRWUpLb1pJaHZjTkFRRUxCUUF3Z2dFck1ROHdEUVlEVlFR
RERBWkJReUJWUVZReExqQXNCZ05WQkFvTUpWTkZVbFpKUTBsUElFUkZJRUZFVFVsT1NWTlVVa0ZE
U1U5T0lGUlNTVUpWVkVGU1NVRXhHakFZQmdOVkJBc01FVk5CVkMxSlJWTWdRWFYwYUc5eWFYUjVN
U2d3SmdZSktvWklodmNOQVFrQkZobHZjMk5oY2k1dFlYSjBhVzVsZWtCellYUXVaMjlpTG0xNE1S
MHdHd1lEVlFRSkRCUXpjbUVnWTJWeWNtRmtZU0JrWlNCallXUnBlakVPTUF3R0ExVUVFUXdGTURZ
ek56QXhDekFKQmdOVkJBWVRBazFZTVJrd0Z3WURWUVFJREJCRFNWVkVRVVFnUkVVZ1RVVllTVU5Q
TVJFd0R3WURWUVFIREFoRFQxbFBRVU5CVGpFUk1BOEdBMVVFTFJNSU1pNDFMalF1TkRVeEpUQWpC
Z2txaGtpRzl3MEJDUUlURm5KbGMzQnZibk5oWW14bE9pQkJRMFJOUVMxVFFWUXdIaGNOTVRrd05q
RTBNakV3TlRFMVdoY05Nak13TmpFek1qRXdOVEUxV2pDQitURW5NQ1VHQTFVRUF4TWVSVk5EVlVW
TVFTQkxSVTFRUlZJZ1ZWSkhRVlJGSUZOQklFUkZJRU5XTVNjd0pRWURWUVFwRXg1RlUwTlZSVXhC
SUV0RlRWQkZVaUJWVWtkQlZFVWdVMEVnUkVVZ1ExWXhKekFsQmdOVkJBb1RIa1ZUUTFWRlRFRWdT
MFZOVUVWU0lGVlNSMEZVUlNCVFFTQkVSU0JEVmpFTE1Ba0dBMVVFQmhNQ1RWZ3hLREFtQmdrcWhr
aUc5dzBCQ1FFV0dWTkJWSEJ5ZFdWaVlYTkFjSEoxWldKaGN5NW5iMkl1YlhneEpUQWpCZ05WQkMw
VEhFVkxWVGt3TURNeE56TkRPU0F2SUZoSlVVSTRPVEV4TVRaUlJUUXhIakFjQmdOVkJBVVRGU0F2
SUZoSlVVSTRPVEV4TVRaTlIxSk5XbEl3TlRDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnRVBB
RENDQVFvQ2dnRUJBSU9HbmI2UnFEeUJoSzNSRHNwekpDZjVtNGd4K2xrQ3pRVHZORXBocjJHZloz
WHlGSERuTWVQNCtJUHo4WGRaelE4V1NqZDdKZU9yNWVmLzlvbUxwNFhkNlBDaDgzV21pVFpuaU5Q
bHVjdFlzNldHREdjbS9HQ0FscDRpSXl1blhYNVRKdk1BamU4UXY4TEltK0VtaXRFLzUrT2NmUExo
RFFBLzlEMzRMM0Q4YWRvSXVVZzhVeWpLM004ZGo2MmhBa0JSRFVGLzBaNHpQaEFQWC9CRVI3bEVk
WlJjRHJUbzFNMGVxOFNNMDkrUTdJdFhrTVlJQmY5UTNKREhmcE9uRDRKYkFKNGRLNjBaa1VRSTB4
bytHNmlzNEVBWHYwMmxpU1JDSWZFdmxKclpId0daT1VhUmNjZmoyZmhSTG9iOTBKYm1sNE5LQ1VS
R2JvaWpvSXVoVGlNQ0F3RUFBYU5QTUUwd0RBWURWUjBUQVFIL0JBSXdBREFMQmdOVkhROEVCQU1D
QTlnd0VRWUpZSVpJQVliNFFnRUJCQVFEQWdXZ01CMEdBMVVkSlFRV01CUUdDQ3NHQVFVRkJ3TUVC
Z2dyQmdFRkJRY0RBakFOQmdrcWhraUc5dzBCQVFzRkFBT0NBZ0VBcjl1SW5hVE1mNlVxU1Q1eHBF
b25zYk9lcWRueVFzRzFaaVlMS3c3bG5qTWprWWtyZW5NYW5GWGtweEhVZVd3OFkvNHk0OGlOY21y
czFBSCtHZDdaZE9KM1hJcUlFeTBDL1NNNEdlbVJ4K1lNamZzaWYyNGR4VE4xZkQ4Y1U4NlcxWTU2
ZTNyRGZnc1I5eVQvc0dteHF2a1VOM3NRRWx5RDIrcWhVWlV5ZEs3aTAzYldJRzVmeXpHSWkxNVlC
aHpFNkFMdVg4cG8yY29VbHdRVjgzMHpSQlBHRGtjb21lanNmS1BqWUtRK3l6VXR3Tys4S2xyMVBV
SG1kbGFHN0d2NGxsV0xOdkttMjFxQWd4ak1raUtITHAxQ3I2NlcxYWhrczhJOFZxc0xhclNLRHpH
ZjQyVnN0UXBPMGhMVjFjV1hrOTIwbmwrbjRodFlnRTdLRFF3cGlvWlhGZVhDZDlLaVpjRVJFbi9n
dkhpNm5xNmF3UEpTN2s2aEJQRkVBdGJtend5a1EzME1OZHRId1VYUktBZjF5cnU5VllHSXMzOEVs
WnlVOEM2SkowTVB4L2YvTjU2eUhZT1lLdFlEKytTVFdnWGpIRDBjL1JQVjVqMW5oalBGaFJNSFpB
dXhPd1F4a3kyOE1RYWsrcGQ3T0Y1Y0RKaUdZZkRRWjdHK3JpR2tob2RJR1Mram1leFdRbjB0cG9a
dDhVK0F5N0w4UDdmZHFjVjlQNThBTXo0RWllM1ZyUHMyTGZwYmhOcEQvMjZBdmdia0U0SXo0SEFP
ZFc5QUgxaW0zQWU4K25XdUlDbmJXY21FeHFjUnF5a00xVTdNWGtPVjIzTDNqdGR2REtjUCt1Q3Vk
d0wrOUlpdDZLNXBDR3ZxdzdlL3VDSzAvT3lodHl4Z0EwTERTMkE9IiBTdWJUb3RhbD0iMS4wMCIg
TW9uZWRhPSJNWE4iIFRvdGFsPSIxLjE2IiBUaXBvRGVDb21wcm9iYW50ZT0iSSIgTWV0b2RvUGFn
bz0iUFVFIiBMdWdhckV4cGVkaWNpb249IjQ0NTkwIj4KICA8Y2ZkaTpFbWlzb3IgUmZjPSJFS1U5
MDAzMTczQzkiIE5vbWJyZT0iNTQxNTgxNSIgUmVnaW1lbkZpc2NhbD0iNjAxIi8+CiAgPGNmZGk6
UmVjZXB0b3IgUmZjPSJSQUxIOTExMDIyVVQzIiBOb21icmU9IlRFU1QiIFVzb0NGREk9IlAwMSIv
PgogIDxjZmRpOkNvbmNlcHRvcz4KICAgIDxjZmRpOkNvbmNlcHRvIENsYXZlUHJvZFNlcnY9IjAx
MDEwMTAxIiBDYW50aWRhZD0iMS4wIiBDbGF2ZVVuaWRhZD0iSDg3IiBVbmlkYWQ9IlVuaXQocyki
IERlc2NyaXBjaW9uPSJ0ZXN0IiBWYWxvclVuaXRhcmlvPSIxLjAwIiBJbXBvcnRlPSIxLjAwIj4K
ICAgICAgPGNmZGk6SW1wdWVzdG9zPgogICAgICAgIDxjZmRpOlRyYXNsYWRvcz4KICAgICAgICAg
IDxjZmRpOlRyYXNsYWRvIEJhc2U9IjEuMDAiIEltcHVlc3RvPSIwMDIiIFRpcG9GYWN0b3I9IlRh
c2EiIFRhc2FPQ3VvdGE9IjAuMTYwMDAwIiBJbXBvcnRlPSIwLjE2Ii8+CiAgICAgICAgPC9jZmRp
OlRyYXNsYWRvcz4KICAgICAgPC9jZmRpOkltcHVlc3Rvcz4KICAgIDwvY2ZkaTpDb25jZXB0bz4K
ICA8L2NmZGk6Q29uY2VwdG9zPgogIDxjZmRpOkltcHVlc3RvcyBUb3RhbEltcHVlc3Rvc1RyYXNs
YWRhZG9zPSIwLjE2Ij4KICAgIDxjZmRpOlRyYXNsYWRvcz4KICAgICAgPGNmZGk6VHJhc2xhZG8g
SW1wb3J0ZT0iMC4xNiIgSW1wdWVzdG89IjAwMiIgVGlwb0ZhY3Rvcj0iVGFzYSIgVGFzYU9DdW90
YT0iMC4xNjAwMDAiLz4KICAgIDwvY2ZkaTpUcmFzbGFkb3M+CiAgPC9jZmRpOkltcHVlc3Rvcz4K
PC9jZmRpOkNvbXByb2JhbnRlPgo=
"""

lst = [random.choice(string.ascii_letters + string.digits) for n in range(30)]
boundary = "".join(lst)
payload = "--" + boundary + "\r\nContent-Type: text/xml\r\nContent-Transfer-Encoding: binary\r\nContent-Disposition: form-data; name=\"xml\"; filename=\"xml\"\r\n\r\n" + xml + "\r\n--" + boundary + "-- "

headers = {
  'Authorization': "bearer " + token[0],
  'Content-Type': "multipart/form-data; boundary=\"" + boundary + "\""
}
response = requests.request("POST", url, data=payload, headers=headers)

response = requests.request("POST", url, headers=headers, data=payload, timeout=20)

print(response.text)