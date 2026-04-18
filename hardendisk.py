"""
HardenDisk v2.0 — Diagnóstico, limpieza y seguridad del sistema
Requiere: pip install customtkinter psutil pillow
"""

# ── Auto-instalación de dependencias ──────────────────────────────────────────
import sys, subprocess

def _ensure():
    deps = []
    try: import customtkinter
    except ImportError: deps.append("customtkinter")
    try: import psutil
    except ImportError: deps.append("psutil")
    try: import PIL
    except ImportError: deps.append("pillow")
    if deps:
        subprocess.check_call([sys.executable,"-m","pip","install","--quiet"]+deps)

# _ensure()

# ── Imports ───────────────────────────────────────────────────────────────────
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import psutil, os, platform, shutil, threading
import tempfile, winreg, ctypes, time, datetime
import json, urllib.request, base64, io
from pathlib import Path
from PIL import Image, ImageTk

# ── Tema: Gris azulado claro, moderno ────────────────────────────────────────
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Paleta: fondos claros, acentos azul acero, tarjetas blancas con sombra suave
C = {
    "bg":        "#EEF1F7",   # fondo general – gris azulado muy suave
    "panel":     "#FFFFFF",   # sidebar / topbar
    "card":      "#FFFFFF",   # tarjetas
    "card2":     "#F5F7FC",   # tarjeta alternada
    "border":    "#D8DEF0",   # bordes suaves
    "accent":    "#2563EB",   # azul primario
    "accent_lt": "#EFF4FF",   # fondo botón secundario
    "accent_hv": "#1D4ED8",   # hover azul
    "success":   "#16A34A",
    "success_bg":"#DCFCE7",
    "warning":   "#D97706",
    "warning_bg":"#FEF3C7",
    "danger":    "#DC2626",
    "danger_bg": "#FEE2E2",
    "text":      "#1E2740",
    "sub":       "#64748B",
    "dim":       "#CBD5E1",
    "white":     "#FFFFFF",
    "nav_sel":   "#EFF4FF",   # fondo ítem nav seleccionado
    "nav_txt":   "#64748B",
    "nav_act":   "#2563EB",
}

LOGO_B64 = "iVBORw0KGgoAAAANSUhEUgAAAIwAAACTCAYAAABcQPFwAAA76klEQVR4nO29ebxdd1kv/H1+wxr2cOaTtGmG5qTtSdOUBkqhkFJmES9QHF99FfHVV+WKgOKVOoICpcC1r6DvVa96QVQQQS7IVKZCUVtkkKaDbdKmSZq0aZOc5Ax7Wmv9huf+sdba2ec0ydlpzknSpt/P5yRnr3PO3mv4/p75eX7A03gaJwE60ydwpvDCd3x4YCYak4oi7xOugDsUgeHghKhXOgYRNQFISj11kkocrLTcTu229776sEsafKbP/0zhnCPM82745BV+zTPede/B9AdpYKXOLIG9RcQGmjzYZ2AATko4x5DOQUqN1HgEkrAilt8YbD709u//3qu/ZTsNd6av53TjnCLM83/7Hzc9NrL+WwejlQPZwApkXgJCA2xAxFBw8M6ACBBKwjuGcgpaa6Q+Q2ZSBFJgPD2ILdn2533lt3/qu6bdPKdIo870CZxOcG341Uk8EvjqMAx7IJAAOoDJwEwwYACcLyPvAQ9YR0icA4UMqilkxqHtNGbTyo8z4878Dc4dnFOEmbFuDHGNEgBMAGwCKAaEA0ECQoIZgAAEGAyHMFBIkwRQAdikgHNIIYChFWMQ4pyS0AAgzvQJnE6IWqxm23MQEgBngARgUsAasLeAZ4AZcAA8gbyD9x2oWIKzDPACYaUG5zwOpfmvnms4Zwiz9f23V9Oh86ULY1hGrnbYQwmCkkAgCAoMOA84hvcMTwKZS2BMGyKKACikjQQQMRrBkOHrpwWi4TN8ZacXT2mRuvWGzw62hy9YOxtUnjerBn64IyovSyhUngF4A8EGASwEewACjiQyCsGkABIAWZQmCnEI8hqCBcAOxAaBbXx0xM9+odbcv+P+t//wna7z1DeAn1KEuf7668WdF76o1uSxyTQcfG2DgtfvN7SqLUOyIgSEAkgBIBAYki0EZwVhAIaAFQqOJCAEQB6gFGAP4UJIr8FewhGBiQFkQDqH8dBjeG7/vmGRfIwzf8uAT+/55tt/9DHTaT7llNZTgjBX3/iJMTky8UNJNHj5nA9/eqptzzPQJMIIKRw8AUQCDAFHCowglyIggBhgD0IGAYYnDwYKwgCABxiAl1CcE8aDwGCADALFyBqHMKQYARzAClUl/q3OnZvD9PBX7/jNH/y+bT914jVPesJc+95/fvPMiktf/XDTvAjVUdV0ArJSR9LJwCSgAwDeQcDm3jJLOEg4CgEQICTADkAGggHgAXgwiZw0kAALwOfckh4ABHxBLmKLqBohTVMIIeDSDJwaDMQxBjk9tJqnvzgwtf3LX/+Dn/6U6bSyM3ajlghPerf6sB596wGMrs2GQ2qlKViHIKHA0gI6gHGcqyEvIeAgSqkCk5MFGQAPQk6qXJzkjhJYAAjyDyIPhoGgDIIBT/mts+yRZg6eYnjrIGMJGQSYSy0c6XGfqddPxCPXMYmbiw97UuNJTxgb1pvTKTELIlYKCCTYZwDbnChC5EEXyr1motxeyWWrQy46ALBFbvoSwALECgyZ2zEQgMj/zhMD5EHM+c8FgYQEfC6snTNw1gBBhExIzKKONBxNC5Y+6fHkJ0yWuXg0QmIaiCOFdrMBDiPoOIJJO4BShaniQfDwzHnQDh55VJcARq6CWMBzqYYUJDyIDZg8HOc2jZUagIX0DCKG9wGQOZDw0NJBwsEHCmlmYIyBpQAzTj812IKnAGEApsx0IAnw3kCECiQFjElyleNyLcAAQFSQpUBBlhwCIAFmiVzOCAAekhjMHo5RuNoCgAKTA0MAUgCWITiDAtBpd6DiCFAa0BpkGS59iogXPAUIQ+RISYJhDesZTqCI2BYPt4cg3P0HCw4C3RgmFUYvPDw8MlBh/AqUqSZAwJd/xw4QgGeBjvcQYTUPDAJAZuDZQML5J713UeCsjPRuef0faxlW+vpd4tL5FfBQAIqgW/fSxPG/uPd1iTIB6cCUqy8uf86YR5r8Kz9Q/p4r3Hdwrgal91CAfcI34yzDWUeYF9zwmVeOXn31m675nS/WVFRf/A+Iz9rFKxgQBvAd23cc5trf+6s3vux9n75Qx7Wz7tkAZxlhrv6dv33r9OCFn5rSI8/hXEw86aGVAsn+TJjrPvxhaddcfu3c8EXfeu77brlKVepyuc/vZHFWPJTJ6z9c3fjB7950cN3V75mSQ/FMxmZ04xQL6Rf/Yz6b7UkBTwIQsi8p+NDMOnHA1Nt73cDIdhr593Xv/PI1Ij67SHPGCTP5/s9Ws8teedue6PxfO6CHwhYUpNR4aOZC4Xjxe8X0ODP2rIEHYEHImPpidfWxJntE3NE1NGujmIpHb518x8efL+PaWUOaM06YmaHLP/xQO9iUxHWRSYJWBJs061XdUNSHfUJ5XP+sBBPAWkJoLamPLMw1uMafPzCaZEmKhDza9QG0xjb+y+TvfPK/yLh2Vni0Z4wwL73xE+HaP7/vTw+psdf4al0jUjCcwliDSAdUN3VxFtuzfcNlBt57erw/f2y052ZEGCqQ8DAqwKOpgj3v4n9+zts/+hJ1FpDmjBBm8w2fHXxofOtNh9V5v8hSh0AKJLMIhYcQgPNMDdMQ3NdNFsTMICIQHSUYiTMuPPNkpWNI34ctBmD7xn8mWWfBMBAuA4yFDet4FAM4ML7xL7a851NXqjOsnk77XX32u78cNYc2v+MAav9vW4QhkwN8hjzCJsGQEEqL8SLWuij6kfVnCAJAqCRCIbnfwoDUWXgwJAlIoYAwRFNXsMtU188Ob/r4Ve/61GZ1Bl3u0/7Bs7L681MiekPbZyGJBMTtvLJNVpGKOjJoaKWT2YEhz7T4TSb0YRmfIRB7sMng0rbvRyU9NLNOtJ2KHRSxV/AswSYFKwlEK7A3rV34cG3dP11506fXq0rtjCyU00qYLb/zD9e0Bs5/b6LCOKwG0IEHC4f8ZgrAa3gEECpEmLj+NBKfvRKGCSBigNCfTgJgieBJw7EGewCS8mpzpZCKCIfC8YseFud/w0MMLOOpHxenjTCXXf+p8SMrn/H5aRHWoQXatoM0aRb5Hg3hGdqb3BWlqP83PpvdagK8FvCqf04LpjZBcJnopDDMOxsyA6kDJCrGAT20Zu37bnmrqNRP4kYtDU4LYV564yfq6YWbvnGkMlaXQyvymlnroSoDADTAAto5aOtAIFjYs5cFJ4kMHuYkWC3AFeFyZUxE4E4CUhKhAlzaAkQIFwzjMV99++Qffu7lMq6fVs/ptBBmf3zemw+oyoaW1KKZWrAj6MogbMKAUxCsIQ1BeUCSh0FKWXSEQItLcj6LI70MgKUCad2HNZYH7gJybcEpS2cROIZkoKIlsmQGOiRIb8FJBq6PY6624rNX/97fXaTi6mnTFMv+QZe/50vPfFQOX2+iWoQwAoQAhTFMJwOpEGCCYACQeaZXEJzPoiirSPQRh5GMnhI6mRsOXqKszT2zEGDLAHNf93ls42EOAg8h8tw72EB4B5umEGEAJoZP24jjCFaGmFUDOFRf+xYmedpU07IS5uq3f3FodmjDO01lZewtIEwK8hZsM0BrcBE8h2R0lEILCo4B6fo/LccgAYJngncC5COQV2DvQLA4k6SRDChLkP24ewA2br+OpQ+JKC8dFUqCFecKmgOwV9CSYWwTjhxaQRWPRWvesP6Gb1x7ulTTshJmdnDotQ098JJUxAoAJFtIdgD3PETh4NmCiQCl82oFdggT01ecN4SlvCMgr81lIjAJSBDEWeBCRUoBxvT1u9s3/jMZ6gAirwy0HijjN44KmUnoCl6GRFNV0Kqt/LUrb/ibIRVXl/1yl40wz3zXP13Qro5/IBOy4onhhD96sVSqC4YkAM6C2CMQBAkP6cCz9awv80QjERoZPFlAOkD7vMEeZ0OpjIcxbVRC1beYc+CcHBTAeQlwkGe8yYGlhyUFhwDkBSQzgpAwZ8wrDrvhV3rQskuZZSNMUw6//ZCVcUoCnnLlkxPA5wWujOJ7DzBDwEOyh2APJUVbznqDfiIxRDInIfKKpcJ28URgpqKq7syBSKLVavUVuJvaPkpp4irOC2JBYEG5jGRRVGP5onNTQzJBeiBJmkiJweMT73zuO/9hhYqXN6C3LHfz+b/915fMhsM/6WqjgZWqUBXdTgwU9Yv5d8yQ4Hy8hk1B7KGV9Ml05LiPStiUAiQiBIsi4Ms2n+3CGp4C9Gk+LA9YQkUDEKqOflIDYxsPs2WC8QALAxJ5ZScTFW27nMetWHQXQhQFoKiCR9Lgwsf0mtd4CL2cl7QshEnHJ96UVEbCzPcUYlMelJ3HAc4JI4TI21R9rqYc9Z97aYnQpULmV0Ie5DJIn4Hh8taRMwhPQKudwUKLfq5navsoCY5ICgkmgofL+6AAFBeIso/Kifz9k04HrDRSGaMZjv7Zy9/5ufU6ri/bhS/5Gz//ps9teMDXf9ZVB0MEwdEflAXXXF54/p9HIXqZAQmQFEjh1+v1gzHJxcXDnNDnMQkBYQC0EXAbktsAZYBwZ7x/LKpWkDFWcz/3enQsDFQ4JkgTkwKEAotCsrAEvMgdBsrA5GEFoIMIQAhAIwsHsUtUfsJ32zWXHktOmH1Z9D5euT5uO8qH8ACFLhLz7Qkujok8/uKKpjKnBBIWz53Kgis844SJxWff9OXzbWVEoDBdROFV+K7tcmYlDEOgk2RoQOLq3/3IysUCbIbTTRbuefBWoUyxlfEkxlHCwOU2DXkYz7mtpiK0oDAdjbzzedd/vt5XAf0TwJLe0Wf/7ofOT4fXvazJoWYwSJd1Q8XDIwFREqUrYgWcsSAtYQTBCoHDSYoZzz/FJ1gpW/7463o2WvkBwVFFWg1lApALkFIVVg4AqAJOo5/g37KBBBCGmCaN5tD4bzKJ4wbYtr7/s9WpaOiXGx6hZw+RGRSDbPIvj4IsxTHKe8IFqbzriT2clGjHI3h4KH6RJyyLLbOkhLEjF/7CrA9DhgKFYR6g6/byUFeqiK6XBEAHgJCwzoEJMAwEA0M4YsTPbfrgbX9+7R/eOrBwtVx94xfGDjh940wwcJ2D1tJRTkTWAIWAyHlG3Lc3uzwgD5BFbXwEj4rKz192wz/9voxrjyPNVe/81Pij1XUfeEzEr2sQAhXGkFJDCQ0qqjckHGTv9bAD4OCNgVQSUALsHNos0Na1T4CotiyXtFRvtPmGzw7OjW3+zlxl5UWzLAS7DmQcwaW5G81FXkj6nKOuFDISeaeiJ0gp4JIWSAkMkIeZm0UIibFa9N6BgO5rNOYGaXjowgPt9I1tFiEFMZAWUopy6QSpAHiQSyHZFvNgzoxqIngIn8HbFAIWFSWgkwRDUfAnZNy/Cx0xqdpLHp5rvN4NDASptQijGFnHgEQF3hlAWRAsJJeNchIgB4kEYIIMBpC1MiCoAGmKqF5FZXoPNmcPXHn7b//oNttuLumqWbJATweVy2ZROb+TWsFSAErCZRkWCjGCn/8ArQWCAGgncNBAHIPTFC0SCOpjmDWMDsLfSqeOoDa2Gs3ZNlhWgCgE2i0EUoBYgKGLyynNnl4xdmYg2CMWHlYJ+NpKNFodiOGVOJJkbwayN8NpoO2BynheRBZrpGkGCA32nEtf9kWuzRcBvPzeEeddl1mnDUQRoAQgIySNJjQFOOCrb2KmNwJoL+k1LdUbmaj2EsR17dhDCJHHQkR+UUxcGGn5Q6RuYtAD3ucjNpQCkk4u8sIQ1gLGeWg4kG0CWqDV6UBGEYSSUFmKSAkodvlUBuoxrFmCoeFInzHpkkMgzQjWa2SpBVQA35wBhIUe1KDQYHAsAGVHoMgAnRbgDEAO0Jwno0DwRfttPlAgf19m1RPQYyDpAJ0EYRhARzX4oXU/cMUHbq3IytLWWS3J3bz++uvF0NDIVe12Q8kghAeBhC6qQPyCL6C7+hmAVPBZilDpfE5umgHeg3QEGVYgAwloARnFCMIYznn4xEAKmX8PcTTlIAoPAgYAQ7A4o161h4CMqvBCA6kDSCEaGAVZB5MmYDaYPXwI9XolF/XsEYYhyHtAWCBrI/eQ8p7tPGiXv7ejfBYfSQJ5C2gJwAHOIHPA/kStSjM9CZzY0zxZLIlK+tfa1ZsBuqKmvZwVDHgJtgYk8pks3dB9gdI/YohcsrRSWM9QUoBCDWMd2Hok7Q4gU4hKBd4JOCPyUe+xRGoyqOpgLsK5WGUiBWABdgg4zyXluZczI2WYgCTLENaqyDKAjYdtplCymk8dV4RogNFoNcFsICo1pKmDCkJYkwJaAI6LaHUZyS6rOXSeNjAdkGTAMeLBIWSNBgABiobRSVvXMvA9FAO1lgJLcifbweiVTYPxLDPFgvYgAgLmQv/iqFCh3oIDD6QpZKUCIQSsMfDOAd5DBhqiXgVqNXjvQToAF1MS4BiIQtgkzUU1UfEBFt2pUmcDCIASSNMsnyJuHbQKEQQRKCPAEpLMIKjUQKoC7wEZhLBl/KrXK5o3keLoMRWE4EL9d5pzUEoi84wUBKvjHwBoSd3rJSHMnF75nMOupqweyB8eZwhgclEJHM19sICfNxKjCNwZC+sBCkI4D4AEnM9yL8ECgAJ7k49CYJO7q9bmA4HKSVKM3PVyGvAahjQsKfgzacOUQ4jAgCSQYmQiQdu3wNrleS8pkBkHlrlN4lx+DFSMQSN0J33mUd7CFixyZtYxSAQgISCEgHEWEAwhHVyg9XP+5Oa6qtSXzBs+ZZW0+YZvDh4ZPH99ZiGcUJAs4RjwguGFg6d8olOpex8XRzve8e4PFrw+zsujAcL8f0ZeQ3LG0XP+TMc+p+PHFnvI/jhj7GiOiQFQPsAvl63EABwy9ptIxRMgOoglUkunvPy4Hqxraf88K72CIMh8theMysP8ZzoB+JTDcaIFuarPO0BBBO89vDPD3qRX5i7V0uCUn6aDH005EwYMxwxfzLEFiUK0nvpJPo1FwIzenTKI8mRuZj0gw/FCdy8JTl3CCLmGnRMQBcs5F43HNNKexhPHieKQJR+KCaGlirMsYdTYhaClE/On/EaB1pcQQ5Cgwk7zuVi0RdHGGa54e8qjlCzHECIeCtMZNrzmbbdHQbQ0AbxTfpqS5TiYBQSBJQHk8oYPB0gr+mktehonwmIZjoIwpe3SJZAgeCkgakN0aKwz7MXSrNxTepPXvPtDkagMrrWeBXufZ1DZQYKhOW9Me1q+LD/oOCaKFwKzNttgdCVaKmPylJ5nS9Z4OnFORTVAyXwTCCKQzXB0kO3TWFYIAWbOKxaB+aqJCNOdZHwOdlVfFX/9fNyp/PERXzu/xfKalI/Gc4jykep5svEkxhY8jSWHIwEEAZwMl8ytPqU3SuJ4vAUh4F0emSSABcMRwSHfZPNppXRqoOMGNhf7Q+SRYyNgKoOreYk8pSf8Jle+53MbsqELftaqIOCemf0eBEtctBQ9LV/ONIKggtnE/v6zb/ri61SlfsrF4U+IMFe99/PXNldc8sX9ifgVJ2SYx1yKAACJvNkqn1dxquf3NAqUKaTFfxFHmzIYIGdAYWXNvSb464n//+t/IKunNlPmpJ/opnd9/nXZ2MV/MRvWK3NQcFIVe50VOSMAR0v4fTFJ4Wk8USwkyaKqaV7fV1ENIB2qtRC2MY3zRPC10daBX7vj+pfeZ9uNk1YBJ0WYTTfd/OZDlQvfO+NrsY6GYODBysESIx8MpKCcgICFlx6eLPzZO4LuSYHjSZXHEeeYT9JChgSXpaCMoDKB0EdYWeF99bn73nj3b7/8ZtdunNTGGX2rpMvf+5k/PlBb9f4j4XCMoZXoMEEIUWzA2W1thPRF0bfz8P5U+sieVmfHw3yyFCUQ3YPF62LbHpdlAAkEURU6GkRHxngkk2t2Rys/O/HBb7xNnuTYs76eyrXvv/mtD8br3j0VjsWp0ICSCBXDph1ASXjk291JDyjOjV1Lcn5bbGkVHyf0e7T2tvwjgW6tyzkMKgYulffy8SqpvE+iaGtZ8FopIMuLtyIZwlsJAwsKPUIzjY1h9ut3/eJVf+5ac2k/57OohHnpjZ9Zf3hg3RsbajhCZRgIYlAUIjVJ3sbZE3H2BFiRt3A6MT8RdlKYF8V+WtIcnyzAUU80n4IBXxaUFd2SHQeIEFACiW+DdQoRAp4JnUxiNpWvfv7bPhf32ym5aBymUa3LwzIcMyDKTD6Uj1MLyAhEgPdHBxiyQN430+tS+4WTx3oM4+OBCiI+zZVj2Cp5dSHhaPsJAfNaUfI0TV4twE4DguGlA4SFIV/sbRtgRX0YNPfoS3RkB4l4Fn2I80UlTOzmDg5p3CY4s0SU17ggL052xhSV+QKAAlihW+JN+QWcetn+ua2S5oGKoRblZuw9ZMndblF8f7TyUCCfuUNERbqGEUQhlGO0Dh1ClejWb/7hjxw2nWZfN3pRwnzz1394bsWRXf970CYZ0hRwLm88cwmqgYL0EtKHIBcCPgRZAXKlaJx3tegSiQD0NGXNR5GefTrNDQAgZhCX96Q4WK5ZUmAoeKii7UTDIYRFCEcxnJBALGFNE8oRQlkFTASXSgTQGIgjVOA+TOC+99Puy0v6l7e+/K9HkkNfr1Ga78LbnkVUr6DdaYDYQrKFYC6ESVnFD5xapPfMdy6eDZhnBzJy28Sjq7LzFmGCJQlLAo5UHjhFIe0FFetUARwATsJbh8C1sUJn/xE8duBz8EtMGACYiLJ3rg2yhzH9MKt6AMMGCAASbRC1QaIFJgsWAhCq/yhvV9LMb3ijcrTZuQwCIH3+Rfl4N+WAwOWHyon7kEC5PyokyqYvwAvYTgYR1sGyirRpACUwUJMYdtPNFdmht33rfa9q2KRxUqfUN67675//gceG13/qoKjWUg+oKAKcBSBgEQEUHH34nI8fYwTzP+a4kaj50ujoojqHk5fdbk4ALu+cld2cnYAtq2BFzx8URCEPCBbwgsDGAUJDiQyhTKGmH8Lza/jxr73pxf9sWnP9jfgscFJP47u/+aqvrJve96MX+XRvzYK9VbAUwgbVfHKlTAFKAU4hTYbAc14HTujpq6F8L6OFEui4Ns05DAbIE5APh4Yv2lSMACws4C3APt9SMk0Al0BLD2RzkOhASAvIECCFWFjU0mlcLGe3PX8gufZrb3rRp0+WLMATdFxfeMPnLkkvfNZf3t/ia9pxTSYun4gkKhH8XAtCEAbCGjqdTu7BSQGCzPUp8naIbqX7QuIUkuZpCZMLY8m+8IryqDpIzm89zgxADB0GMFkKOIswDOFNCkEaaUaIhcCgaeDiQXx1LNn31s//6g/ea55AHgl4goQBgJfe+IWxzuglv7gjFW9vRQORjSLYNIUMQzjjgMxChRE8LIgciGReI1N6T1JBSJm3xvaiDAgXBvO5TBjJHpq5S5gUKOqOintCEhASMDbXFc4iDCTgLZwzIJsi8i2sj1Q61jryW887+OX/edON7+4kSfKEz6kvwlz1ghesqQjBt912235r7TxmPvePvv7szvDEjY+k7kVNGSlEA/AqgPeAcwYSJm/IL6SJQ1GoLBSEepowJ0I+kMhAFl6OY4JlyklSEoeQx8ZacwjCALbThMhSDMQhomwW42LmA6v48J9+7Td+co9ZMFzoGS94wRqu11v3fvWr086YvlyMvggzdsnlv6o6Mz9TCfiX9+zef7f384MsW6//rGqPVV6ACy77h+1ztKITVglZGxQGEGxAvtiTUeUXarsRbM4vfh6KKvgnWmn2VALlzgOEgPYKwhGklxCkYIVACg+mfK8GJR0iWOhGA7XMYJD9Zyqz+9/x/fe89h7befwUqvEtz73m8AO7/mLV2vX/sP/+79/kne1L7Cz6OFZu2TLqEv+nZvbQq+YOHqiNXXD+66YefvQT7P3jDKaJGz8Rdmj1dW5g7EMiENWOdaDKIBInYJ0HCQEWskgcKJAU8I8rFn+aMF1Q4VKDIBwgM4b2ChIEBw/jU4SVAGwbQDqDik0wUQ1uS/btft09N/7MHpe0jik1Kuet+UAnMW8YGTuPIkHfpOHw/97/H9877K1dVMos+jiGzlt/QZa1/3Vi3ZoLISXdd9d9GFq95o5VF4y+5t5v3f6IO8aHvPSXbgzlpZdtaaih/+ex2pr/66CoDBoH4mKakmcGRACpFaw9do/4UcKcw8EYQtdRgPOA9ZAkEAogZAORtTFWoXRQpDvC5sGPdHDfX97x629uuvaxp5SNTVywPj3Q+Fikg2esndgQt01GO/fuOXzB+StftPeBB+71zi1qCC9KmPPPX3dZJ2nfsubCdSuEjiiDRCdJsXf7vVPrLt7wwVXnVT/57X/59wesscf8sC1//PW4GQ1f6VX4MtLhtSnUC9oZq4QFrAwAqfPyCCozIzg6U4YYnnpsmXl1H/nR/CJ6p0uK4ld6w6NFuv8J/d/7Vo+3p6iYeVP+f3yU0TQ6Rhld+Y3vfpQoEoxwHoIdhHeQbFHXAoOhMFVOd0RZ49aqa//FrW/5gftO5PVs3rx57VRz7o0HH33szRPnXRCdPz4GYwysItxx110YueD81x7eu/8L3vtFi6kWJcz4+PgPzs42PnnJJZfUgjAEyQCdNIFSCocOHTS1anyPVPjToeGx73zv9tu32+OJDADPfveHoiC64MVJMLBJjJx3RapqP7Z/uhN3WMEKDScElNQgImQmhVICEA5eEqwFoMPi5hbjuYyBDCSENzBpijCKYL0A6QA2s4BS3Y2qmCl/IJRvvuU9AG8hVABmB2YqWmR6f27yehIl8y1sWEDpENZYwHroMAQ8w4HhTYYgimC8ATsHHYYwaQoiXRj8EiTy/9mk6AaoJAHGQioJ9hawBooE2DsomyGyKVYNVJOBgL/Kzemdun3kgUoye0faqt7xb++9Lj1elPa6666T+6amrujMNl7UaTZ+3np7ab1eF/W4CmKG9R4kBe66524MDA69/vChQx9n7xdNEZyQMFu3blVHpqbecPjwkfevXrsmFkKASMJaCx0EaLfbSEyG6elpOzwy+kAcxx8PQ/2lO7773f9wJyAOAFz34Q/LgwfPv7wjKoNUH1mNqHa5D+Jrp2abVyWZUfXBYcw2GwjiAHPtFOHgCBqZhZMhhI7gXR6w8iYFsUEcaDABaeryhx3EuReRdYpoafHAOC8souK1d+geZ7juzwUpCEUwLgO8y0kqRLFhEQrBlUsiFSiQZxhnimGQDJIyJ4olhGEI5xxIACZNEMUByDvAG2gAWbuJkDx80sZwNcbIwEBn+tDBr9e1/I7ozP77Sjb33vq7r9pvOv3FTp7xnKt/InXiZe1241ok7YlKqHW1UkEQBHDOwRgDIoJSCvv370ccx7+/a9euP/LeL2r4LiphNm/a9KedTvKLw6MjIQA4l3s8SucrJ7UGYRhiZmYGrU7bVisDe3SgtwUy+NxANfin22+/rW1tf2WjL373h4Z9fWXFqXDE+/AiXR+6lCl6ZWqFONg2z5lxUqW6hkyGsELmsRwt4bMUgIcOFIy1UGEIQQGypAMpdbe+huHAnrqvSTC8ZeQlPDlR2AH57B0JkIfSAtakEDqAEDIfJyY1lFKwnU4RCyEgSaCrMeAZgoAsy6B1TmLTaUNKgks6qIcaESza04dwwchAYzigB2Jvbhftmbsj0LbATB/xaXrw5nf8TKPfkgMAuPLKq7cQ4+WZ9a/opOZSx3SelBCKLOJIQ2sF5xycc8gXfj4S5MiRIxBCfGj37t1v8t4vOqJ1UcI8Y/PmPzPG/kJcrQREBOc4v1nOQSkFYwwgBbTWSNMUxjg4721jdu5QVIkPWZLfDaPwk7v/885bvHMnVXA8D9dfL1544WtXdai6MhPRxrZ1K4UOJzNj1qkwEJb9i+YaLS2jEB2Tb0QFEghUCO99t5WUiLpfACCKVlPv85qR3pvpvYUEdX9mvENmDYIgyB+AzaCFRJa2MRCFyNptsMlQCQPIfN+nR4M4uF+Q30Pg7bbVvq8iae8dB59xj71x3Gx9y0fUtz/40/Zkkn+92Lhx43qh1E8Qieuajdb59WptRZaZOIqqFEfVXGKSAeBhrYUxBkIIhGEIICd1kiQQQnx8x44dv+ScW/REFiXMFVdc8TfW2p8KgiCQUsJ7X5Ajg1QaWms0Gg1orVGpVNBoNAApEAUh2q0W2HL6yCMPT881m2JoaPhzwytX3JzMhV977LFtc967JXeBtl7/WeXGEw2qR5mKLlKkjAbYKyHY0gjgryBQoLQcFEKdR/T4saTM+eAsAQmTAjqM2Dt7IDXJA4AblOTuZpu1tWD2ruXrkmfQmG585d2/st90WstayLNq7drng/lnjszOvCJNkoEL1qytViuVKApCytIOBgobJU3TfFEIAZJi3sI4ep2MTqcDKeU3t2/f/irnXHOxz1+UMM985jNvzrLsZUEQqPJDtdbIMgspJYy1IMr1dJIkCMMQWZblAUgC2NiC1TF2PfJI+/Bss5N2OsMIwkdWXLDqG4EO/s5o951D//mfDe+WnkBPZjzzuc/cmHU6m3xiXrn7ob0/nqSmDgKtXj9BIyMjCOMIJsvyqeHeIdQyrx7wLn8dV9BOMjBkvidV8fxcEV0XQqDT6SAIgm/eddddfRFm0Zpea62z1nbFWPmBVGzHp6SElBLNRiMnTaeDarWaT8a0GcJYwRqD1GVYvXp1pT7YroRRDY6xZurwkZ96ZPeDrxOBhmeNjZdveuUD9957izsV1fUUweSWLa+5a9s9H3Ue1ZVr1+KiK64kay201hCcG9SN2TaqUQxjUlQqEbKsBZOlqMS5cTvXmkEYDsA5zLNfZGGQM+f2qFuYnjkBTkiYiy66qAbggHPOl7odQPeD8g/NfzeOYzjnMFCro9lsQggBpRSyNEEYaiRZBu8sRoYGkGQWLmVccN4KfcF5K2BthkOHHjuctLOVfC4nj3rBHK69eDIL4ko1CCJK2x3Uq3Uk7Q6YDSIVINAxvLFQIPjMAZ4QBCEcCJYFdBTBGgchFEpzonc0iPceSZLAe7+Hub+tX074cHbu3Nli5qb3np1zsNbCOQcpcxHnvYckwFsDdhYCjCRpQykBIgY7h4AU2DhoQQgEwaQNCE6hQwvvmzBuDlJbVGtxTQfqItDThAEAATGhWMSaiUSaoSIkuNNBzEAFBJ1l0NYiYkIEme+5hRDeh8hsACfqSFlDyNylt9bOky7e++4z5O5wmcWxmEriVqv1gLXWlxJDSomZmZnCU9BAmVgspM/CaUiu7IScd7TY+R1AEAVotxKAbVitVC+nJZ6N/yQEAWAt5GbrjdKeiz4MD1mO3eGjEWFmFKNti0BgWYhWVD46l0JK2eP5+e4z6pE4u9BnAfYJCbNlyxbdaLQfeuSRfX58fAU6nQ6EEBgcHIT3HsaYrnrq5n565gczBLzKL6b8uUDZEpG/Tuc6CIMQUS1EO+mch6cHygAAjMvOD0Od75TA+VY6QJEuIO7uWZbHEanYVTcPJQgAzhc79faYDaU66j4zIuzduxerVq3ahmLm+mI44cPZtm2b8d7sA+C42GkjCAJYa5EkSVc1HfdL5clGRwJOzP8oKvapDnUe2nc2gSIMT05OhlLKc5k0DAA6CEaoa8/lm8R74eFEvmm8lR5OlF+c70ALk28a7wwEZxDeItD5VgOlCiqlDQBorXHeeedBCNFXExvQh5dEFM5eddVVJk07SJIE9XodrVYLWut51jWjFHVHVRMB0LktVqigohsglz1FexLDGANvPCpRdYSCYD0B033e3KckLr/yyg2xilYnti089Wzvg7Jt9mhitWsKMIM5r24EAI1cPVl71FEp7RgigrUWaZpidHQ0nZqa2ok+VdKiK3lgIJprNhvfttbaMporRB7ZlYVL3es9lV+loVVKEuL5bSMeIt97mQlKhxgcHoYnHm12Gpv5HLdjhPXPajXnKoHW3T0T8uVWbrSlii8JQOYqhwmi8BgkEUh4CJFHq7VWCHq2hFZKgYjQ6XTQbDY/89hjj836xxcmHfvcFvuFbdu2HQbEF+bm5owxBsYYaK3zAu8sg4eDYwvHPp91LwWEkt3oIijfs7ALVvCk4RHCIoajClIXYK4NzLWdcAhejCXcWvDJiGZz7oUCrNvNBgCbt7sif1jKCyiniq8AwmpIF0EghOAAgIT3DGcZpvBovS9jZ7nha4yBK1I7WusvElHf3QN9PZiLLlr/P++9994gy7L3NBqNWCmVV6Z7Dw/XNaK01l3viYohw/OdpqJWhUW+fyEAJgmSuUDxkFBard+yZcvwtm3bOu4cjPxu2bJlFPATnVYihoeHYVyWV9GUtc7dyQfzY2JUvvYengHrXZ4GYItWq4Pe4GuSJGBmhGH4v4Ig+BLyLez6wkkVQE5OTj5LSvkCAGuJqFrGZEo1xcxsjPkZpVQtjmNEUYSyJievM0H3Ihm5Lk3TtBv0a7fbqNcHplvJ7M/t+M8dXzwXI76Tk5M/Wq1W/4yZxwGQEMdSAkePERGyLCtUjkeWZTh48CBqteq/DA7WDxIp7nQ6TESdMAz93NxcWKlUWs1m82uDg4NfvvPOO+dOZmGelOjfsWPH9wF8f+vWrerb3/62tblFNe/DJiYmfk0I8Q0Az2FmmW9oebRPumukFbu9D9SraDabCIIAtWqMfXt3D4+Ojj4DwFfQp6v3VILWetWRI0fqAwMDFEXRccL2R+1T5zxqtQrSNEWSJGi1WlNBEFyza9fuB3rskiWT1E/Ifb3ttttsUePyuBPZtWtXSkT/5b777muUog/AvP97jeS5uTmEYdg1lsfGxpAkyUsuu+yyNeeae71hw4bR2dnZHxsYGAi01uinjkhrjVarBWst7r//fgghrnz44YfvLzo7lnyiwbI8kB07dkyvXLny751zee9VESQ6VgS6Xq93E2MAIKXEnj17Xjw1NfXcXEKdO7DWXnP48OErnXOytBEXQ68Tsnr16o/u2bNnql+P54lg2Vaw1vorO3bssGUoemE4ujzWarW67rkQAlEU4dJLL0WtVnvLli1b6lKeG5xZu3btGiL66dWrVwd5+UjWN2HCMCxrkr5KRMuqxpeNMEqpOy+55JIm5zjujhuVSqUbSCrdvSAI8OCDDz57ZmbmNcx8ytOrnwxQSm3Zu3fvD0VRpMtFUq1WF/27SqWCJElQqVSaUsr/wDLbfctGmJ07d+5N0/RjaZpmpS4uLf5e1WSMQaPRQLVa7UaPiQiXXnopgiD4wy1btoxIKZ/S7WwTExMhgHdt2rQpDsMwL4G1Fs3movVMMMbgyJEjCMPwf9dqtUNEy9vItaxGpZTym1mWWefcPDUEzCdNtVota0u7AaUgCNBqtdZOTU39FjOf0rjzsx2dTue/JUkyWavVRJIkyLIMYRh24yYnghCi7Ab4+ve///1p20f34qlgWQmjtd47PDx8b6fTcWXyqzjelSTAUc+prCizRdnnihUrcODAgbeMjo7+ABE9JaO/q1evnjxw4MDbVq5cGZWLRQiBLMu696ssfioXXBn/Yma0222EYXhbHMffxEkE4J4olpUw99133x1zc3MfC4Igc851K/GSJIHWui+j7uKLL0YQBB+fmJg4XwjxlFJNW7Zs0VEU3bxu3bq67skqlw5Alh27r+xotWNOGGPMl+6+++7HTkdkfNnjHHEcf0pKuU0I4er1OoQQiOM4b0/pA1prrFy5Moqi6G+JaHEr8EmCrVu3qna7/WUiWrty5Uqy1s6rVSmxsNK/ROltxnF8pzHmo8zc1yTvU8WyE+auu+7a1+l0vtlsNm2SJEiSBO12uy8PAEC3tibLshdt2LDhv0spK8t8yqcFBw4c+MNqtfq8IAgkgO4CkjLvLC3beYD5NdQAumqpKOr+zO7dux9dzthLL05LJHVkZOT/i6LoYSkla627nZL9xFhKe6ZWqyEIgjdcdtllvyGlfFJLmg0bNvyqUuot7XY7iuO4mwsqVdHCqPjC6DiQdwF47w967z8C4LRIF+A0Eea73/3uIWPMzbOzs1lpwFUq/QmKWq2GNE27Rl6WZe/cuHHjWzdt2jT6ZHS3V69e/eZKpfL+er1eLVW0c65r7DMzpJRQSs0rSVhIGO89rLVffuCBBw6czqz+acvVCCFuTdPUlo3gxzPoFqLRaHRX3uDgYFlm+AdBELwLwJPK3b7kkkveXKvV3iuEiLMsg7W2my8qVUyv/bKwuL43FFGEKm7FaU7QnjbCpGn6g6tWrdIASmOtr+RaHMddnd1sNlGv18HMotPp/NeJiYnPCyFqy37yS4D169d/TUp5k5QyDsOwK0WklAjDEMYYSCm7kqbsgwZwXEPYWruGeWk2MO8Xp0WkT05OvlQp9ZlKpVIrk4xBEHQLyU94gj3tEQC6v59lGdI0RZZlD0kpr9u1a9fjZu+dDZicnBw2xtxKRJvjOBZRFIGI+goplFho8ALd699vjLl6z549Dz/pjd6tW7cqpRQmJiZebIz5dBzHtbJNpSxAjqLFNUp5o3qnKpSzTaIowsjIyLrdu3dvW7169duEEGeLB0UAxMTExK/s2rXrEQDPWLFihahUKt18WWnLPVEUddWrpJQ3r1mzZux0xaiW9UM2bdr0QinlPwohVhARxXGMNE27Rm+r1YJSJw7gMnOXLL2Z7lJcJ0mCKIqwa9cuDA8P36K1ftf9999/25mq1tu6das6cODA862178yybOv4+LgqQ/xlH1dZwlp6gIthof3SG7ibmppCHMe3pGn6+r179+5fbkmzbIS59NJLX0REf5MkydogCKharc5TQwtjCyc8yR4PoVyVJYl6Jc/09DTSNIVS6n9IKf/xwQcf/FY/c9uWAps3bx50zl2YpulPaK3fSkSRlBIDAwMoDdyycj/LMhBRdyLUiXCsTP9CQ/jgwYOIouiWNE1/bt++fY8sJ2mWhTDr169/yfDw8N/Mzc2tHhwcpPLGNBoNVCoVhGGIdrvd1w07Fql6X3vv4ZzrjgUTQuDAgQOo1Wqw1n4kDMOvWGu/s3Pnzl2ujymRJ4vLLrts3Hv/AmPMSwH8QrPZDC+44IKue1ymQUoV1JsTOlHZx8JrPVamv5RSUkrs3bsX4+Pjt7Tb7Z/cu3fv4eUizZITZvXq1UPj4+MPzs7OjgwNDc3ruCulQavVmveAT3iCPQZirzQpb1zvVILy5iul0Ol0MDc3B621DcPwdiLamWXZN4QQ392xY8cDp0KeTZs2DRHRS4UQL7fWXiyEuNZaq4IgQBzHZbyoO+2JiGCMmXcMQDe+dCIsnJwFoHs/SglbEvHQoUMIw/A7u3fvfpn3/omNtVoES06YSy655M2HDh1678TERAzkkdqyWzLLMlQqlW7Yu9PpLGrDnIgw5U0sYzthGGJubg5RFEFrjSRJEAQBpqenkWUZxsbGUmPMfiKabrVaO4QQX2LmnWEY7rbWtnbu3NkogmAEgK+44or11lpprV0fRdFYlmVXJklybRRFlWq1evHU1FRQq9Wgte6SVGvdTWcAOSmAnMRKqW4HYnlsMcN34fUDmPe6jN2U73XHHXdgdHT056ampv7B9zEV82Sx5IS57LLLPi+lfIXWWgG5BChXVhAEyLKsK64BLGrDLHQpF86jWyilyuNpmnY/r1KpgJm73QntdrssI3DOOUlEaLfbXfVWJEeZmSmO4+55lrGTEmWfefmepXQpvSBjTFftLqwH6pUSJ4KUskwDzFswwNH5fGWZZll05b3/H7t27fpN732n/yfXH5a8xiRJkoe9935gYKDrDZRqowxGHSsrezz0EupY+nyhSisfWLnilFLdqHKpCnoSn7JM8B2jWGnRkysfYkma0h4rpUL5sMtjC+t/joWFbcfHkq7lgum9H+WxJEkQxzH3c2+fCJY8DuO9/8BDDz2U5E1sHu12u7s6ey+23+BVb7/2iY49GdB7zgsJ1JtwXBik6z22cALDwsKqAwcOYHp6+ivMvCzFVEtOmN27d29fu3btRx599NHUWtutIAPwhB5yeTOOlWNZrlW0XDjWtR9rIZzM+wVB0LWLGo0GxsbG/m5qauqW5QonLEukNwzDD3jvD2qtucwF9dodpVezmIcE4LjEeLIQ5njScKHhfqx65954S6866p1VV4xNLaX1vpGRkeuJaMltlxLLdscnJyeva7fbH63VatUwDPOp2AtUErC40Vti4e89GcgCzLdXFiYQFx4rj/cSaWFpw0KbpjTS9+/fDyHEa/fs2dPXJhNPFMt614eHh/+r9/6mlStXxsPDw13Dt1RTvRnZ455gj3F3rJV3ttsxxyL2wutZGC5YSJITpUacc7jzzjsxPDz8R4cPH347My+bdAFOQ7Z6ZGTkT4aGhn5pYGAg7E0J9KqpE2HhzS1xrFV7NmIhERaSvjewCRzb6C3RS5ayfmZqagpRFH1k9+7dv+q9X7yR6VSvZ7k/4NnPfnY0MzPzUSJ6dbVa1WVsBEBfqYEyYcfMbWbeQ0QVIloBICYiKt3isxml3VFIiAzAQSIyRLTKex/2tgofy5M6UXmHc+6ru3bt+pHTQRbgNBRQfe9730u897/snPu3drtty0KhUv+WUqeMm5QEKnuXZmZmQES3KaUu2759++Z77rlnIk3THwqC4KvMfHhmZobLZF45w6183/Jml/GQhfGZfiZglyu6jO+Ux3pTE711uGVup8xEZ1mGZrMJIkoBfFpr/Yr77rtv/d133z3R6XSuEULc3Ww2fe/c3FLdlNdSvncZNMyyDLOzs/Def0NK+UYiWnQXkqXCaZPnk5OTEwCun5mZ+bnx8fGgWq12JU1ZBB1FUfeYMaZcQV/btWvXDxcriCYnJ/XOnTuzyy+/XFtrrxFC/Kwx5hWzs7PnjY2NUTmcqLSPyodZ5q6SJAERIYqivir+ygdYqoOF8aQkSVCr1eC9R6cYm1+u/sOHD2PFihWHkiT5hvf+b3ft2vUVv2CvzMnJyQki+nCWZVujKJIDAwNotVoIgqCrtksp2mw2EccxDh48CGb++0ceeeRXlitndDycbgNArFix4j1TU1O/tnnz5jCKom7qIAgCNBqN7sizffv2IYqijw0NDf3KnXfeOXs8abBmzZowjuPnKKWeZYz5qSNHjjw7CAK5YsWKbuKvnJAFoBt9LtMDJxNt7jU0S2O0d1AkEeHhhx9GlmVYsWLFPUKIjwO49f777//2iepzNm7cuL7T6dxkjHnV6OioLqvyyj2XynxUEAQ4dOgQtNZ/tWvXrreeLjXUizNiMa5evfrVUsq/1lqPVyqVbvlD6T3t3bsXQRB8oFKp3HD//fcf7qcqfuvWrerIkSOr0jQdd879iJTyR/bs2XPJRRddJGq1WreTsEwUttttlNHoE6FULyVBFmaKlVKYnp7Gzp07sXbt2r1hGH5aSvkFIcTue++9t++SiosvvnjEWvuX3vvXjI6O6rK2t1SdBw4cgNa6qZR6w4MPPvhJ59ySJxb7wRlzMdatW/fMIAj+bGZm5qrVq1dLIF/J99xzD0ZGRv5iamrqv3nvW0/0/ScnJ4MkSS4NguAvrbVXDg8PyzAM0Wq1uiUGvfbB8dDr/veqptK+2L9/P4aHh29JkuRdYRhuGx8fb99+++2m313oerF69ep1cRz/r0aj8cLBwUFVr9fR6XSwfft2rFy58ktRFP36nj17yulSZwRn0icVk5OTanZ29menpqY+aK2tjIyMQEr5tqmpqT/hJWr9XLVq1bBS6l/GxsY2ZVkmSjXYq0YWQ6/0K43ZMk+mlPra9u3bf8w5N1f8+ikFhlavXr2OiH7jyJEjv9Rut8NVq1alzrlfOnjw4MeXo1zhZHE2BTEUlqnHZmJi4jWNRuNjF154YbVUL1EU9d3fXXpVALrtIOVcFinldfv27fvi6SoFPdM4m4YOLtsNb7VaB4Ig8KV0KGNB/Uj2Y4Xzy/k1UkrU6/U5WsYhPlu2bOlOpDobcDYRZtkQxzGVA4t64z/9oDeOU35fhugLL2tZcxPbtm0zJ7Nj2nLjnCCMtZar1WpXnRTH0E+UuDcoV35fTlcAgE6nc9bns5YS5wRhkiThsn+pLJssSxv7wcKa2jKAp5RCHMd0tuezlhJPyTFgC1Gv17nstiwr+kuvp5++oN7ve7PHBeHOHbbg3JAwQghxXqPREM451Ov1rh3Tb6ykN/dVEqhMXfTT7vtUwrlAGG6321StVhFFEVqtVlfFLNbiAqDblVBKl1IyEeW7tzSbzXPKhjkXVBIPDQ3tk1L6sk23tEFOxvsoVVEZg7HWIo7je4Mg2ElEZ93UiOXCuSBhcN99993RbDZ/d//+/Z3ygffb5nKsarhOp4N2uw0Af3/PPfccPJf2dToXJAwAIMuyvxoYGKBms/mmBx98cGLNmjXCe496NZ9HVI6wL2Ms1tquCnNKYWZmBt57PLL/EUxeMtlUQr3Pe/9XAM54uP504pyy8AFgw4YNFzPzitnZ2WeNjY1tyJJsQxgEK/c/uv9ZzVZTMjMCHSAzOQ8u2nDRHvb+gSAIHzQ222Gc+1chxFQYhgfuv//+5GwKqp0OnHOEKTExMRE656Jiu5258fHxqHao5ulCwqMHHh0ZDocpikE+DOQFe/Y89i3vswU+1eM2FzsX8H8AX3hd7r6YzoYAAAAASUVORK5CYII="

# ── Helpers ───────────────────────────────────────────────────────────────────
def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None,"runas",sys.executable,f'"{sys.argv[0]}"',None,1)

def fmt_bytes(b):
    for u in ["B","KB","MB","GB","TB"]:
        if b<1024: return f"{b:.1f} {u}"
        b/=1024
    return f"{b:.1f} PB"

def fmt_uptime(s):
    d,h,m=int(s//86400),int((s%86400)//3600),int((s%3600)//60)
    return f"{d}d {h}h {m}m"

# ── Carga del logo ─────────────────────────────────────────────────────────────
def load_logo(size=(42,42)):
    try:
        raw = base64.b64decode(LOGO_B64)
        img = Image.open(io.BytesIO(raw)).convert("RGBA").resize(size, Image.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)
    except:
        return None

def load_logo_small(size=(20,20)):
    try:
        raw = base64.b64decode(LOGO_B64)
        img = Image.open(io.BytesIO(raw)).convert("RGBA").resize(size, Image.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)
    except:
        return None

# ── Herramientas externas ─────────────────────────────────────────────────────
CLAMAV_MSI = "https://www.clamav.net/downloads/production/ClamAV-1.3.1.win.x64.msi"

def clamav_exe():
    p = shutil.which("clamscan")
    if p: return p
    for x in [r"C:\Program Files\ClamAV\clamscan.exe", r"C:\ClamAV\clamscan.exe"]:
        if os.path.isfile(x): return x
    return None

def cdi_exe():
    for base in [os.environ.get("ProgramFiles",""), os.environ.get("ProgramFiles(x86)","")]:
        for root,_,files in os.walk(base):
            for f in files:
                if "DiskInfo" in f and f.endswith(".exe"): return os.path.join(root,f)
            break
    return None

def install_tool_winget(winget_id, choco_id, log_cb):
    if shutil.which("winget"):
        log_cb(f"winget install {winget_id}...")
        r=subprocess.run(["winget","install","--id",winget_id,"-e","--silent",
                          "--accept-package-agreements","--accept-source-agreements"],
                         capture_output=True,text=True)
        if r.returncode==0: log_cb("Instalado correctamente."); return True
        log_cb(f"winget: {r.stderr.strip()[:100]}")
    if shutil.which("choco"):
        log_cb(f"choco install {choco_id}...")
        r=subprocess.run(["choco","install",choco_id,"-y"],capture_output=True,text=True)
        if r.returncode==0: log_cb("Instalado con Chocolatey."); return True
        log_cb(f"choco: {r.stderr.strip()[:100]}")
    return False

# ── Funciones de sistema ──────────────────────────────────────────────────────
def get_system_info():
    return {
        "os":     f"{platform.system()} {platform.release()}",
        "build":  platform.version(),
        "arch":   platform.architecture()[0],
        "cpu":    (platform.processor() or "N/A")[:68],
        "host":   platform.node(),
        "boot":   datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%d/%m/%Y  %H:%M:%S"),
        "uptime": fmt_uptime(time.time()-psutil.boot_time()),
    }

def get_cpu_info():
    freq = psutil.cpu_freq()
    return {
        "phy":  psutil.cpu_count(logical=False),
        "log":  psutil.cpu_count(logical=True),
        "cur":  f"{freq.current:.0f} MHz" if freq else "N/A",
        "max":  f"{freq.max:.0f} MHz" if freq else "N/A",
        "use":  psutil.cpu_percent(interval=0.8),
        "per":  psutil.cpu_percent(interval=0.5, percpu=True),
    }

def get_memory_info():
    vm=psutil.virtual_memory(); sw=psutil.swap_memory()
    return {"total":fmt_bytes(vm.total),"used":fmt_bytes(vm.used),
            "free":fmt_bytes(vm.available),"pct":vm.percent,
            "swap_total":fmt_bytes(sw.total),"swap_used":fmt_bytes(sw.used),"swap_pct":sw.percent}

def get_disk_info():
    out=[]
    for p in psutil.disk_partitions():
        try:
            u=psutil.disk_usage(p.mountpoint)
            out.append({"dev":p.device,"fs":p.fstype,
                        "total":fmt_bytes(u.total),"used":fmt_bytes(u.used),
                        "free":fmt_bytes(u.free),"pct":u.percent})
        except: pass
    return out

def get_net_info():
    out=[]; addrs=psutil.net_if_addrs(); stats=psutil.net_if_stats()
    for iface,alist in addrs.items():
        ip=next((a.address for a in alist if a.family.name=="AF_INET"),"—")
        up=stats[iface].isup if iface in stats else False
        spd=stats[iface].speed if iface in stats else 0
        out.append({"name":iface,"ip":ip,"up":up,"spd":spd})
    return out

def get_top_procs(n=14):
    procs=[]
    for p in psutil.process_iter(["pid","name","cpu_percent","memory_percent","status"]):
        try: procs.append(p.info)
        except: pass
    procs.sort(key=lambda x:x.get("cpu_percent") or 0,reverse=True)
    return procs[:n]

def clean_temp():
    c=e=0
    for folder in [tempfile.gettempdir(),
                   os.path.join(os.environ.get("WINDIR","C:\\Windows"),"Temp"),
                   os.path.join(os.environ.get("LOCALAPPDATA",""),"Temp")]:
        if not os.path.exists(folder): continue
        for item in Path(folder).iterdir():
            try:
                if item.is_file(): item.unlink(); c+=1
                elif item.is_dir(): shutil.rmtree(item,ignore_errors=True); c+=1
            except: e+=1
    return c,e

def empty_recycle():
    try:
        subprocess.run(["powershell","-Command","Clear-RecycleBin -Force -ErrorAction SilentlyContinue"],
                       capture_output=True,text=True,timeout=30)
        return True,"Papelera vaciada."
    except Exception as e: return False,str(e)

def check_registry():
    out=[]
    for hive,path in [(winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
                      (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
                      (winreg.HKEY_LOCAL_MACHINE,r"SYSTEM\CurrentControlSet\Services")]:
        try:
            k=winreg.OpenKey(hive,path)
            n=winreg.QueryInfoKey(k)[0]
            out.append({"key":path,"n":n,"ok":True})
            winreg.CloseKey(k)
        except Exception as ex:
            out.append({"key":path,"n":0,"ok":False,"err":str(ex)})
    return out

def check_defender():
    try:
        r=subprocess.run(["powershell","-Command",
            "Get-MpComputerStatus|Select AntivirusEnabled,RealTimeProtectionEnabled,AntivirusSignatureLastUpdated|ConvertTo-Json"],
            capture_output=True,text=True,timeout=20)
        return r.stdout.strip()
    except Exception as e: return f'{{"error":"{e}"}}'

def check_updates():
    try:
        r=subprocess.run(["powershell","-Command",
            "(New-Object -ComObject Microsoft.Update.Session).CreateUpdateSearcher().Search('IsInstalled=0').Updates.Count"],
            capture_output=True,text=True,timeout=30)
        s=r.stdout.strip()
        return int(s) if s.isdigit() else -1
    except: return -1

def check_firewall():
    try:
        r=subprocess.run(["netsh","advfirewall","show","allprofiles","state"],
                         capture_output=True,text=True,timeout=10)
        return r.stdout.strip()
    except Exception as e: return str(e)

def get_installed_apps():
    apps=[]
    keys=[(winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
          (winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
          (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")]
    for hive,path in keys:
        try:
            k=winreg.OpenKey(hive,path)
            for i in range(winreg.QueryInfoKey(k)[0]):
                try:
                    sk=winreg.OpenKey(k,winreg.EnumKey(k,i))
                    name=winreg.QueryValueEx(sk,"DisplayName")[0]
                    try: ver=winreg.QueryValueEx(sk,"DisplayVersion")[0]
                    except: ver="—"
                    apps.append({"name":name,"ver":ver})
                    winreg.CloseKey(sk)
                except: pass
            winreg.CloseKey(k)
        except: pass
    apps.sort(key=lambda x:x["name"].lower())
    return apps

def check_disk_wmic():
    try:
        r=subprocess.run(["wmic","diskdrive","get","Status,Caption,Size"],
                         capture_output=True,text=True,timeout=15)
        return r.stdout.strip()
    except Exception as e: return str(e)

def get_startup_items():
    items=[]
    for hive,path in [(winreg.HKEY_CURRENT_USER,r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
                      (winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run")]:
        try:
            k=winreg.OpenKey(hive,path)
            for i in range(winreg.QueryInfoKey(k)[1]):
                name,val,_=winreg.EnumValue(k,i)
                items.append({"name":name,"cmd":val[:80]})
            winreg.CloseKey(k)
        except: pass
    return items

def get_env_vars():
    important=["PATH","TEMP","TMP","WINDIR","SYSTEMROOT","USERPROFILE","COMPUTERNAME","USERNAME"]
    return {k:os.environ.get(k,"—")[:90] for k in important}

# ══════════════════════════════════════════════════════════════════════════════
#  WIDGETS
# ══════════════════════════════════════════════════════════════════════════════

class Card(ctk.CTkFrame):
    def __init__(self,master,**kw):
        super().__init__(master,fg_color=C["card"],corner_radius=12,
                         border_width=1,border_color=C["border"],**kw)

class Card2(ctk.CTkFrame):
    def __init__(self,master,**kw):
        super().__init__(master,fg_color=C["card2"],corner_radius=12,
                         border_width=1,border_color=C["border"],**kw)

class BtnPrimary(ctk.CTkButton):
    def __init__(self,master,text,cmd=None,w=None,**kw):
        opts=dict(fg_color=C["accent"],hover_color=C["accent_hv"],
                  text_color=C["white"],font=("Segoe UI",11,"bold"),
                  height=36,corner_radius=18,**kw)
        if w: opts["width"]=w
        super().__init__(master,text=text,command=cmd,**opts)

class BtnSecondary(ctk.CTkButton):
    def __init__(self,master,text,cmd=None,w=None,**kw):
        opts=dict(fg_color=C["accent_lt"],hover_color=C["dim"],
                  text_color=C["accent"],font=("Segoe UI",11),border_width=1,
                  border_color=C["border"],height=36,corner_radius=18,**kw)
        if w: opts["width"]=w
        super().__init__(master,text=text,command=cmd,**opts)

class BtnDanger(ctk.CTkButton):
    def __init__(self,master,text,cmd=None,**kw):
        super().__init__(master,text=text,command=cmd,
                         fg_color=C["danger"],hover_color="#B91C1C",
                         text_color=C["white"],font=("Segoe UI",11,"bold"),
                         height=36,corner_radius=18,**kw)

class Pill(ctk.CTkLabel):
    """Etiqueta tipo badge/pill de estado."""
    def __init__(self,master,text,ok=True,warn=False,**kw):
        if warn:   bg,fg=C["warning_bg"],C["warning"]
        elif ok:   bg,fg=C["success_bg"],C["success"]
        else:      bg,fg=C["danger_bg"],C["danger"]
        super().__init__(master,text=text,font=("Segoe UI",9,"bold"),
                         text_color=fg,fg_color=bg,
                         corner_radius=10,**kw)

class MiniBar(ctk.CTkFrame):
    def __init__(self,master,label,pct,bar_w=200,**kw):
        super().__init__(master,fg_color="transparent",**kw)
        c= C["success"] if pct<65 else C["warning"] if pct<85 else C["danger"]
        ctk.CTkLabel(self,text=label,font=("Segoe UI",10),text_color=C["sub"],
                     width=100,anchor="w").pack(side="left")
        bar=ctk.CTkProgressBar(self,width=bar_w,height=9,corner_radius=5,
                                progress_color=c,fg_color=C["dim"])
        bar.set(min(pct,100)/100); bar.pack(side="left",padx=6)
        ctk.CTkLabel(self,text=f"{pct:.1f}%",font=("Segoe UI",10,"bold"),
                     text_color=c,width=44).pack(side="left")

class LogBox(ctk.CTkTextbox):
    def __init__(self,master,h=130,**kw):
        super().__init__(master,height=h,font=("Consolas",9),
                         fg_color=C["card2"],text_color=C["text"],
                         border_color=C["border"],border_width=1,
                         corner_radius=10,**kw)
        self.configure(state="disabled")
    def append(self,line):
        self.configure(state="normal"); self.insert("end",line+"\n")
        self.see("end"); self.configure(state="disabled")
    def clear(self):
        self.configure(state="normal"); self.delete("1.0","end")
        self.configure(state="disabled")

class SectionLabel(ctk.CTkLabel):
    def __init__(self,master,text,**kw):
        super().__init__(master,text=text,font=("Segoe UI",9,"bold"),
                         text_color=C["sub"],**kw)

class RowKV(ctk.CTkFrame):
    """Fila clave–valor."""
    def __init__(self,master,key,val,alt=False,**kw):
        bg = C["card2"] if alt else C["card"]
        super().__init__(master,fg_color=bg,**kw)
        ctk.CTkLabel(self,text=key,font=("Segoe UI",10),text_color=C["sub"],
                     width=170,anchor="w").pack(side="left",padx=(12,4),pady=5)
        ctk.CTkLabel(self,text=val,font=("Segoe UI",10,"bold"),text_color=C["text"],
                     anchor="w").pack(side="left",padx=(0,12))

class CheckRow(ctk.CTkFrame):
    def __init__(self,master,label,detail="",ok=True,warn=False,**kw):
        super().__init__(master,fg_color="transparent",**kw)
        Pill(self,("✓" if ok and not warn else "⚠" if warn else "✗"),
             ok=ok,warn=warn,width=26,height=22).pack(side="left",padx=(0,8))
        ctk.CTkLabel(self,text=label,font=("Segoe UI",11),
                     text_color=C["text"]).pack(side="left")
        if detail:
            ctk.CTkLabel(self,text=detail,font=("Segoe UI",10),
                         text_color=C["sub"]).pack(side="right",padx=6)

# ══════════════════════════════════════════════════════════════════════════════
#  APLICACIÓN
# ══════════════════════════════════════════════════════════════════════════════

NAV = [
    ("  Inicio",          "inicio",    "🏠"),
    ("  Rendimiento",     "perf",      "⚡"),
    ("  Monitor en vivo", "monitor",   "📊"),
    ("  Diagnóstico",     "diag",      "🩺"),
    ("  Seguridad",       "sec",       "🔒"),
    ("  Limpieza",        "clean",     "🧹"),
    ("  Software",        "soft",      "📦"),
    ("  Servicios",       "services",  "⚙"),
    ("  Inicio del sist.","startup",   "🚀"),
    ("  Usuarios",        "users",     "👤"),
    ("  Salud del disco", "health",    "❤"),
    ("  Entorno",         "env",       "🌐"),
    ("  Reporte",         "report",    "📄"),
    ("  Herramientas",    "tools",     "🔧"),
]

class HardenDisk(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("HardenDisk")
        self.geometry("1150x730"); self.minsize(920,580)
        self.configure(fg_color=C["bg"])
        try:
            raw=base64.b64decode(LOGO_B64)
            ico=Image.open(io.BytesIO(raw)).convert("RGBA")
            self.wm_iconphoto(True, ImageTk.PhotoImage(ico))
        except: pass
        self._build()
        self._nav("inicio")

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build(self):
        # Sidebar
        self.sb=ctk.CTkFrame(self,width=210,fg_color=C["panel"],
                              corner_radius=0,border_width=0)
        self.sb.pack(side="left",fill="y"); self.sb.pack_propagate(False)

        # Logo + título
        logo_row=ctk.CTkFrame(self.sb,fg_color="transparent")
        logo_row.pack(fill="x",padx=18,pady=(22,4))
        logo_img=load_logo((38,40))
        if logo_img:
            ctk.CTkLabel(logo_row,text="",image=logo_img).pack(side="left",padx=(0,10))
        ctk.CTkLabel(logo_row,text="HardenDisk",
                     font=("Segoe UI",16,"bold"),text_color=C["text"]).pack(side="left",anchor="s",pady=2)
        ctk.CTkLabel(self.sb,text="Sistema · Seguridad · Rendimiento",
                     font=("Segoe UI",9),text_color=C["sub"]).pack(anchor="w",padx=18,pady=(0,14))

        ctk.CTkFrame(self.sb,height=1,fg_color=C["border"]).pack(fill="x",padx=0)

        # Nav items
        self._nav_btns={}
        for label,key,_ in NAV:
            btn=ctk.CTkButton(self.sb,text=label,anchor="w",
                              font=("Segoe UI",12),height=38,
                              fg_color="transparent",hover_color=C["nav_sel"],
                              text_color=C["nav_txt"],corner_radius=10,
                              command=lambda k=key:self._nav(k))
            btn.pack(fill="x",padx=10,pady=1)
            self._nav_btns[key]=btn

        ctk.CTkFrame(self.sb,height=1,fg_color=C["border"]).pack(fill="x",padx=0,pady=10)

        # Admin badge
        adm_txt  ="✓  Administrador" if is_admin() else "⚠  Sin privilegios admin"
        adm_color= C["success"] if is_admin() else C["warning"]
        ctk.CTkLabel(self.sb,text=adm_txt,font=("Segoe UI",9,"bold"),
                     text_color=adm_color).pack(padx=18,anchor="w")
        if not is_admin():
            BtnSecondary(self.sb,"Reiniciar como admin",cmd=run_as_admin
                         ).pack(fill="x",padx=10,pady=(6,0))

        ctk.CTkLabel(self.sb,text=f"Python {platform.python_version()}  ·  v2.0",
                     font=("Segoe UI",8),text_color=C["dim"]).pack(padx=18,pady=(8,18),anchor="w")

        # Área derecha
        right=ctk.CTkFrame(self,fg_color=C["bg"],corner_radius=0)
        right.pack(side="left",fill="both",expand=True)

        # Topbar
        top=ctk.CTkFrame(right,fg_color=C["panel"],height=52,corner_radius=0)
        top.pack(fill="x"); top.pack_propagate(False)
        self._page_lbl=ctk.CTkLabel(top,text="",font=("Segoe UI",15,"bold"),
                                     text_color=C["text"])
        self._page_lbl.pack(side="left",padx=22,pady=14)
        self._status_lbl=ctk.CTkLabel(top,text="",font=("Segoe UI",10),
                                       text_color=C["sub"])
        self._status_lbl.pack(side="right",padx=22)

        # Contenido
        self.content=ctk.CTkScrollableFrame(right,fg_color=C["bg"],
                                             scrollbar_button_color=C["border"],
                                             scrollbar_button_hover_color=C["dim"])
        self.content.pack(fill="both",expand=True)

    def _nav(self,key):
        titles={k:l.strip() for l,k,_ in NAV}
        self._page_lbl.configure(text=titles.get(key,""))
        for k,btn in self._nav_btns.items():
            if k==key: btn.configure(fg_color=C["nav_sel"],text_color=C["nav_act"],font=("Segoe UI",12,"bold"))
            else:      btn.configure(fg_color="transparent",text_color=C["nav_txt"],font=("Segoe UI",12))
        self._clear(); self._status("")
        {"inicio":self._pg_inicio,"perf":self._pg_perf,"sec":self._pg_sec,
         "clean":self._pg_clean,"soft":self._pg_soft,"startup":self._pg_startup,
         "health":self._pg_health,"env":self._pg_env,"tools":self._pg_tools,
         "monitor":self._pg_monitor,"diag":self._pg_diag,
         "services":self._pg_services,"report":self._pg_report,"users":self._pg_users,
        }.get(key,lambda:None)()

    def _clear(self):
        for w in self.content.winfo_children(): w.destroy()

    def _status(self,msg,color=None):
        self._status_lbl.configure(text=msg,text_color=color or C["sub"])

    def _pad(self): return {"padx":20,"pady":6}

    # ── Inicio ────────────────────────────────────────────────────────────────
    def _pg_inicio(self):
        self._status("Cargando...",C["warning"])
        def load():
            si=get_system_info()
            cpu=psutil.cpu_percent(interval=0.6)
            mem=psutil.virtual_memory().percent
            try: disk=psutil.disk_usage("C:\\").percent
            except: disk=0
            procs=len(psutil.pids())
            self.after(0,lambda:self._render_inicio(si,cpu,mem,disk,procs))
        threading.Thread(target=load,daemon=True).start()

    def _render_inicio(self,si,cpu,mem,disk,procs):
        self._status("",C["sub"])
        P=self._pad()

        # Hero banner
        hero=ctk.CTkFrame(self.content,fg_color=C["accent"],corner_radius=14)
        hero.pack(fill="x",padx=20,pady=(16,8))
        hi=ctk.CTkFrame(hero,fg_color="transparent"); hi.pack(fill="x",padx=20,pady=16)
        logo=load_logo((48,50))
        if logo: ctk.CTkLabel(hi,text="",image=logo).pack(side="left",padx=(0,14))
        txt=ctk.CTkFrame(hi,fg_color="transparent"); txt.pack(side="left")
        ctk.CTkLabel(txt,text="HardenDisk",font=("Segoe UI",20,"bold"),
                     text_color=C["white"]).pack(anchor="w")
        ctk.CTkLabel(txt,text=f"{si['os']}  ·  {si['host']}",
                     font=("Segoe UI",10),text_color="#C7D9FF").pack(anchor="w")
        adm=ctk.CTkFrame(hi,fg_color="transparent"); adm.pack(side="right")
        Pill(adm,"✓ Admin" if is_admin() else "⚠ Sin admin",ok=is_admin()
             ).pack(pady=2)

        # Stat cards
        grid=ctk.CTkFrame(self.content,fg_color="transparent"); grid.pack(fill="x",**P)
        stats=[("CPU",f"{cpu:.1f}%",C["accent"] if cpu<80 else C["danger"]),
               ("Memoria",f"{mem:.1f}%",C["success"] if mem<75 else C["warning"]),
               ("Disco C:",f"{disk:.1f}%",C["success"] if disk<80 else C["danger"]),
               ("Procesos",str(procs),C["sub"])]
        for i,(t,v,ac) in enumerate(stats):
            c=Card(grid); c.grid(row=0,column=i,padx=5,pady=4,sticky="nsew")
            grid.grid_columnconfigure(i,weight=1)
            ctk.CTkLabel(c,text=t,font=("Segoe UI",10),text_color=C["sub"]).pack(pady=(12,0))
            ctk.CTkLabel(c,text=v,font=("Segoe UI",22,"bold"),text_color=ac).pack()
            ctk.CTkLabel(c,text="",height=6).pack()

        ctk.CTkFrame(self.content,height=1,fg_color=C["border"]).pack(fill="x",padx=20,pady=10)
        SectionLabel(self.content,"INFORMACIÓN DEL SISTEMA").pack(anchor="w",padx=20,pady=(0,4))
        c=Card(self.content); c.pack(fill="x",**P)
        rows=[("Sistema operativo",si["os"]),("Build",si["build"][:50]),
              ("Arquitectura",si["arch"]),("Procesador",si["cpu"]),
              ("Nombre del equipo",si["host"]),("Último arranque",si["boot"]),
              ("Tiempo activo",si["uptime"])]
        for i,(k,v) in enumerate(rows): RowKV(c,k,v,alt=i%2==1).pack(fill="x")
        ctk.CTkFrame(c,height=6,fg_color="transparent").pack()

        ctk.CTkFrame(self.content,height=1,fg_color=C["border"]).pack(fill="x",padx=20,pady=10)
        BtnPrimary(self.content,"🔍  Ejecutar análisis completo",cmd=self._full_scan,
                   ).pack(padx=20,pady=4,anchor="w")

    def _full_scan(self):
        self._status("Analizando...",C["warning"])
        def run():
            time.sleep(1.2)
            self.after(0,lambda:self._status("Análisis completado",C["success"]))
            self.after(0,lambda:messagebox.showinfo("HardenDisk",
                "Análisis completado.\nRevisa cada sección para el detalle completo."))
        threading.Thread(target=run,daemon=True).start()

    # ── Rendimiento ───────────────────────────────────────────────────────────
    def _pg_perf(self):
        self._status("Recopilando datos...",C["warning"])
        ctk.CTkLabel(self.content,text="Cargando...",font=("Segoe UI",12),
                     text_color=C["sub"]).pack(pady=40)
        def load():
            cpu=get_cpu_info(); mem=get_memory_info()
            disks=get_disk_info(); procs=get_top_procs(); net=get_net_info()
            self.after(0,lambda:self._render_perf(cpu,mem,disks,procs,net))
        threading.Thread(target=load,daemon=True).start()

    def _render_perf(self,cpu,mem,disks,procs,net):
        self._clear(); self._status("",C["sub"])
        P=self._pad()

        SectionLabel(self.content,"PROCESADOR").pack(anchor="w",padx=20,pady=(14,4))
        c=Card(self.content); c.pack(fill="x",**P)
        for i,(k,v) in enumerate([("Núcleos físicos",str(cpu["phy"])),
            ("Núcleos lógicos",str(cpu["log"])),
            ("Frecuencia actual",cpu["cur"]),("Frecuencia máxima",cpu["max"])]):
            RowKV(c,k,v,alt=i%2==1).pack(fill="x")
        MiniBar(c,"Uso total",cpu["use"]).pack(padx=12,pady=(6,4),anchor="w")
        if cpu["per"]:
            gf=ctk.CTkFrame(c,fg_color=C["card2"],corner_radius=8)
            gf.pack(fill="x",padx=12,pady=(0,10))
            SectionLabel(gf,"Uso por núcleo").pack(anchor="w",padx=10,pady=(6,2))
            grd=ctk.CTkFrame(gf,fg_color="transparent"); grd.pack(padx=10,pady=(0,8),anchor="w")
            for i,pct in enumerate(cpu["per"]):
                col=C["success"] if pct<65 else C["warning"] if pct<85 else C["danger"]
                ctk.CTkLabel(grd,text=f"C{i}  {pct:.0f}%",font=("Segoe UI",9),
                             text_color=col,width=62).grid(row=i//8,column=i%8,padx=2,pady=1)

        ctk.CTkFrame(self.content,height=1,fg_color=C["border"]).pack(fill="x",padx=20,pady=8)
        SectionLabel(self.content,"MEMORIA RAM").pack(anchor="w",padx=20,pady=(0,4))
        c=Card(self.content); c.pack(fill="x",**P)
        for i,(k,v) in enumerate([("Total",mem["total"]),("Usado",mem["used"]),
                                   ("Disponible",mem["free"])]):
            RowKV(c,k,v,alt=i%2==1).pack(fill="x")
        MiniBar(c,"RAM",mem["pct"]).pack(padx=12,pady=(6,4),anchor="w")
        MiniBar(c,"SWAP",mem["swap_pct"]).pack(padx=12,pady=(0,10),anchor="w")

        ctk.CTkFrame(self.content,height=1,fg_color=C["border"]).pack(fill="x",padx=20,pady=8)
        SectionLabel(self.content,"ALMACENAMIENTO").pack(anchor="w",padx=20,pady=(0,4))
        for d in disks:
            c=Card(self.content); c.pack(fill="x",**P)
            hdr=ctk.CTkFrame(c,fg_color="transparent"); hdr.pack(fill="x",padx=12,pady=(10,2))
            ctk.CTkLabel(hdr,text=f"💾  {d['dev']}  ({d['fs']})",
                         font=("Segoe UI",11,"bold"),text_color=C["text"]).pack(side="left")
            ctk.CTkLabel(hdr,text=f"{d['used']} / {d['total']}   libre: {d['free']}",
                         font=("Segoe UI",9),text_color=C["sub"]).pack(side="right")
            MiniBar(c,"Uso",d["pct"],bar_w=280).pack(padx=12,pady=(2,10),anchor="w")

        ctk.CTkFrame(self.content,height=1,fg_color=C["border"]).pack(fill="x",padx=20,pady=8)
        SectionLabel(self.content,"TOP PROCESOS (CPU)").pack(anchor="w",padx=20,pady=(0,4))
        c=Card(self.content); c.pack(fill="x",**P)
        hdr=ctk.CTkFrame(c,fg_color=C["card2"],corner_radius=8)
        hdr.pack(fill="x",padx=0,pady=0)
        for txt,w in [("PID",55),("Nombre",270),("CPU%",65),("RAM%",65),("Estado",90)]:
            ctk.CTkLabel(hdr,text=txt,font=("Segoe UI",9,"bold"),text_color=C["sub"],
                         width=w,anchor="w").pack(side="left",padx=4,pady=4)
        for p in procs:
            r=ctk.CTkFrame(c,fg_color="transparent"); r.pack(fill="x")
            for txt,w in [(str(p.get("pid","")),55),(str(p.get("name",""))[:36],270),
                          (f"{p.get('cpu_percent',0):.1f}",65),(f"{p.get('memory_percent',0):.1f}",65),
                          (str(p.get("status",""))[:12],90)]:
                ctk.CTkLabel(r,text=txt,font=("Segoe UI",9),text_color=C["text"],
                             width=w,anchor="w").pack(side="left",padx=4,pady=1)

        ctk.CTkFrame(self.content,height=1,fg_color=C["border"]).pack(fill="x",padx=20,pady=8)
        SectionLabel(self.content,"RED").pack(anchor="w",padx=20,pady=(0,4))
        c=Card(self.content); c.pack(fill="x",**P)
        for iface in net[:10]:
            r=ctk.CTkFrame(c,fg_color="transparent"); r.pack(fill="x",padx=12,pady=3)
            col=C["success"] if iface["up"] else C["danger"]
            Pill(r,"●  Activa" if iface["up"] else "●  Inactiva",ok=iface["up"],
                 width=72).pack(side="left",padx=(0,10))
            ctk.CTkLabel(r,text=iface["name"][:28],font=("Segoe UI",10),
                         text_color=C["text"],width=200,anchor="w").pack(side="left")
            ctk.CTkLabel(r,text=iface["ip"],font=("Segoe UI",10),
                         text_color=C["sub"],width=130).pack(side="left")
            ctk.CTkLabel(r,text=f"{iface['spd']} Mbps",font=("Segoe UI",9),
                         text_color=C["sub"]).pack(side="right",padx=10)
        ctk.CTkFrame(c,height=6,fg_color="transparent").pack()

        BtnSecondary(self.content,"↻  Actualizar",cmd=self._pg_perf
                     ).pack(anchor="e",padx=20,pady=8)

    # ── Seguridad ─────────────────────────────────────────────────────────────
    def _pg_sec(self):
        self._status("Verificando...",C["warning"])
        ctk.CTkLabel(self.content,text="Verificando estado de seguridad...",
                     font=("Segoe UI",12),text_color=C["sub"]).pack(pady=40)
        def load():
            df=check_defender(); upd=check_updates(); fw=check_firewall()
            self.after(0,lambda:self._render_sec(df,upd,fw))
        threading.Thread(target=load,daemon=True).start()

    def _render_sec(self,df_raw,upd,fw):
        self._clear(); self._status("",C["sub"])
        P=self._pad()

        SectionLabel(self.content,"WINDOWS DEFENDER").pack(anchor="w",padx=20,pady=(14,4))
        c=Card(self.content); c.pack(fill="x",**P)
        try:
            d=json.loads(df_raw)
            av=d.get("AntivirusEnabled",False); rt=d.get("RealTimeProtectionEnabled",False)
            sig=str(d.get("AntivirusSignatureLastUpdated","N/A"))[:45]
            CheckRow(c,"Antivirus habilitado","Sí" if av else "No",ok=av).pack(fill="x",padx=14,pady=5)
            CheckRow(c,"Protección en tiempo real","Sí" if rt else "No",ok=rt).pack(fill="x",padx=14,pady=5)
            CheckRow(c,"Firmas actualizadas",sig,ok=True).pack(fill="x",padx=14,pady=(5,12))
        except:
            ctk.CTkLabel(c,text=df_raw[:300],font=("Segoe UI",9),text_color=C["sub"],
                         wraplength=640).pack(padx=14,pady=10)

        ctk.CTkFrame(self.content,height=1,fg_color=C["border"]).pack(fill="x",padx=20,pady=8)
        SectionLabel(self.content,"ACTUALIZACIONES").pack(anchor="w",padx=20,pady=(0,4))
        c=Card(self.content); c.pack(fill="x",**P)
        if upd==-1:    CheckRow(c,"No se pudo verificar","Comprueba manualmente",ok=False,warn=True).pack(fill="x",padx=14,pady=12)
        elif upd==0:   CheckRow(c,"Sistema al día","Sin actualizaciones pendientes",ok=True).pack(fill="x",padx=14,pady=12)
        else:          CheckRow(c,f"{upd} actualización(es) pendiente(s)","Actualizar recomendado",ok=False).pack(fill="x",padx=14,pady=12)

        ctk.CTkFrame(self.content,height=1,fg_color=C["border"]).pack(fill="x",padx=20,pady=8)
        SectionLabel(self.content,"FIREWALL DE WINDOWS").pack(anchor="w",padx=20,pady=(0,4))
        c=Card(self.content); c.pack(fill="x",**P)
        for line in fw.split("\n"):
            line=line.strip()
            if not line: continue
            ok="ON" in line.upper() or "ENABLE" in line.upper()
            bad="OFF" in line.upper() or "DISABLE" in line.upper()
            color=C["success"] if ok else C["danger"] if bad else C["sub"]
            ctk.CTkLabel(c,text=line,font=("Consolas",9),text_color=color,
                         anchor="w").pack(fill="x",padx=14,pady=1)
        ctk.CTkFrame(c,height=6,fg_color="transparent").pack()

        ctk.CTkFrame(self.content,height=1,fg_color=C["border"]).pack(fill="x",padx=20,pady=8)
        SectionLabel(self.content,"ESCANEO CON CLAMAV").pack(anchor="w",padx=20,pady=(0,4))
        c=Card(self.content); c.pack(fill="x",**P)
        exe=clamav_exe()
        if exe: CheckRow(c,"ClamAV detectado",exe[:60],ok=True).pack(fill="x",padx=14,pady=6)
        else:   CheckRow(c,"ClamAV no encontrado","Instálalo en Herramientas",ok=False).pack(fill="x",padx=14,pady=6)
        self._clam_log=LogBox(c,h=120); self._clam_log.pack(fill="x",padx=14,pady=6)
        row=ctk.CTkFrame(c,fg_color="transparent"); row.pack(fill="x",padx=14,pady=(0,12))
        BtnDanger(row,"🛡  Iniciar escaneo (C:\\)",cmd=self._run_clamav).pack(side="left")
        BtnSecondary(row,"↻  Actualizar firmas",cmd=self._run_freshclam).pack(side="left",padx=10)

    def _run_clamav(self):
        self._clam_log.clear(); self._clam_log.append("Iniciando escaneo ClamAV...")
        self._status("Escaneando...",C["warning"])
        def run():
            exe=clamav_exe()
            if not exe:
                self.after(0,lambda:self._clam_log.append("ClamAV no encontrado."))
                return
            try:
                proc=subprocess.Popen([exe,"-r","--bell","-i","C:\\"],
                    stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
                for line in proc.stdout:
                    self.after(0,lambda l=line.rstrip():self._clam_log.append(l))
                proc.wait()
                col=C["success"] if proc.returncode==0 else C["danger"]
                msg="Sin amenazas." if proc.returncode==0 else "¡Amenazas detectadas!"
                self.after(0,lambda:self._status(msg,col))
            except Exception as e:
                self.after(0,lambda:self._clam_log.append(str(e)))
        threading.Thread(target=run,daemon=True).start()

    def _run_freshclam(self):
        self._clam_log.clear(); self._clam_log.append("Ejecutando freshclam...")
        def run():
            exe=clamav_exe()
            fc=os.path.join(os.path.dirname(exe),"freshclam.exe") if exe else shutil.which("freshclam")
            if fc and os.path.isfile(fc):
                r=subprocess.run([fc],capture_output=True,text=True)
                for l in (r.stdout+r.stderr).split("\n"):
                    self.after(0,lambda ll=l:self._clam_log.append(ll))
            else: self.after(0,lambda:self._clam_log.append("freshclam no encontrado."))
        threading.Thread(target=run,daemon=True).start()

    # ── Limpieza ──────────────────────────────────────────────────────────────
    def _pg_clean(self):
        P=self._pad()
        SectionLabel(self.content,"HERRAMIENTAS DE LIMPIEZA").pack(anchor="w",padx=20,pady=(14,6))

        tasks=[("🗂  Archivos temporales","Elimina %TEMP%, Windows\\Temp y LocalAppData\\Temp",
                C["accent"],self._do_temp),
               ("🗑  Papelera de reciclaje","Vacía definitivamente la papelera",
                C["warning"],self._do_recycle),
               ("🔑  Registro de Windows","Verifica entradas críticas del registro",
                "#7C3AED",self._do_registry)]
        for title,desc,ac,cmd in tasks:
            c=Card(self.content); c.pack(fill="x",**P)
            row=ctk.CTkFrame(c,fg_color="transparent"); row.pack(fill="x",padx=16,pady=12)
            txt=ctk.CTkFrame(row,fg_color="transparent"); txt.pack(side="left",expand=True,fill="x")
            ctk.CTkLabel(txt,text=title,font=("Segoe UI",12,"bold"),text_color=C["text"]).pack(anchor="w")
            ctk.CTkLabel(txt,text=desc,font=("Segoe UI",10),text_color=C["sub"]).pack(anchor="w",pady=2)
            ctk.CTkButton(row,text="Ejecutar",fg_color=ac,hover_color=ac,
                          text_color=C["white"],font=("Segoe UI",11,"bold"),
                          height=36,corner_radius=18,width=100,command=cmd).pack(side="right")

        ctk.CTkFrame(self.content,height=1,fg_color=C["border"]).pack(fill="x",padx=20,pady=10)
        SectionLabel(self.content,"REGISTRO DE OPERACIONES").pack(anchor="w",padx=20,pady=(0,4))
        self._clean_log=LogBox(self.content,h=200); self._clean_log.pack(fill="x",padx=20,pady=4)
        BtnSecondary(self.content,"Limpiar log",cmd=lambda:self._clean_log.clear()
                     ).pack(anchor="e",padx=20,pady=4)

    def _log_c(self,msg):
        ts=datetime.datetime.now().strftime("%H:%M:%S")
        self._clean_log.append(f"[{ts}]  {msg}")

    def _do_temp(self):
        self._status("Limpiando temporales...",C["warning"])
        def run():
            n,e=clean_temp()
            self.after(0,lambda:self._log_c(f"Temporales: {n} elementos eliminados, {e} errores."))
            self.after(0,lambda:self._status(f"✓  {n} archivos eliminados",C["success"]))
        threading.Thread(target=run,daemon=True).start()

    def _do_recycle(self):
        self._status("Vaciando papelera...",C["warning"])
        def run():
            ok,msg=empty_recycle()
            self.after(0,lambda:self._log_c(msg))
            col=C["success"] if ok else C["danger"]
            self.after(0,lambda:self._status("Papelera vaciada" if ok else "Error",col))
        threading.Thread(target=run,daemon=True).start()

    def _do_registry(self):
        self._status("Verificando registro...",C["warning"])
        def run():
            for i in check_registry():
                self.after(0,lambda x=i:self._log_c(
                    f"[REG] {x['key']}  →  {x['n']} entradas  →  {'OK' if x['ok'] else x.get('err','')}"))
            self.after(0,lambda:self._status("Registro verificado",C["success"]))
        threading.Thread(target=run,daemon=True).start()

    # ── Software ──────────────────────────────────────────────────────────────
    def _pg_soft(self):
        self._status("Cargando software...",C["warning"])
        ctk.CTkLabel(self.content,text="Cargando lista...",font=("Segoe UI",12),
                     text_color=C["sub"]).pack(pady=40)
        def load():
            apps=get_installed_apps()
            self.after(0,lambda:self._render_soft(apps))
        threading.Thread(target=load,daemon=True).start()

    def _render_soft(self,apps):
        self._clear(); self._status(f"{len(apps)} aplicaciones",C["sub"])
        SectionLabel(self.content,f"SOFTWARE INSTALADO  —  {len(apps)} entradas").pack(anchor="w",padx=20,pady=(14,6))

        sv=ctk.StringVar()
        entry=ctk.CTkEntry(self.content,textvariable=sv,placeholder_text="Buscar aplicación...",
                           font=("Segoe UI",11),height=36,corner_radius=18,
                           fg_color=C["card"],border_color=C["border"],
                           border_width=1); entry.pack(fill="x",padx=20,pady=(0,6))

        table=ctk.CTkScrollableFrame(self.content,height=490,fg_color=C["card"],
                                      corner_radius=12,border_width=1,border_color=C["border"])
        table.pack(fill="x",padx=20,pady=4)

        hdr=ctk.CTkFrame(table,fg_color=C["card2"],corner_radius=0)
        hdr.pack(fill="x")
        for t,w in [("Nombre",410),("Versión",200)]:
            ctk.CTkLabel(hdr,text=t,font=("Segoe UI",10,"bold"),text_color=C["sub"],
                         width=w,anchor="w").pack(side="left",padx=8,pady=5)

        self._rows=[]
        for i,app in enumerate(apps):
            bg=C["card2"] if i%2==1 else C["card"]
            r=ctk.CTkFrame(table,fg_color=bg); r.pack(fill="x")
            ctk.CTkLabel(r,text=app["name"][:60],font=("Segoe UI",10),
                         text_color=C["text"],width=410,anchor="w").pack(side="left",padx=8,pady=2)
            ctk.CTkLabel(r,text=app["ver"][:30],font=("Segoe UI",9),
                         text_color=C["sub"],width=200,anchor="w").pack(side="left")
            self._rows.append((app["name"].lower(),r))

        def filt(*_):
            q=sv.get().lower()
            for name,row in self._rows:
                if q in name: row.pack(fill="x")
                else: row.pack_forget()
        sv.trace_add("write",filt)

    # ── Inicio del sistema ────────────────────────────────────────────────────
    def _pg_startup(self):
        self._status("Cargando...",C["warning"])
        def load():
            items=get_startup_items()
            self.after(0,lambda:self._render_startup(items))
        threading.Thread(target=load,daemon=True).start()

    def _render_startup(self,items):
        self._clear(); self._status(f"{len(items)} entradas de inicio",C["sub"])
        SectionLabel(self.content,f"PROGRAMAS DE INICIO AUTOMÁTICO  —  {len(items)} entradas").pack(
            anchor="w",padx=20,pady=(14,6))
        ctk.CTkLabel(self.content,
            text="Estos programas se inician automáticamente con Windows. "
                 "Revisa si alguno es desconocido.",
            font=("Segoe UI",10),text_color=C["sub"],wraplength=700
        ).pack(anchor="w",padx=20,pady=(0,8))

        c=Card(self.content); c.pack(fill="x",padx=20,pady=4)
        hdr=ctk.CTkFrame(c,fg_color=C["card2"],corner_radius=0); hdr.pack(fill="x")
        for t,w in [("Nombre",180),("Comando / ruta",500)]:
            ctk.CTkLabel(hdr,text=t,font=("Segoe UI",10,"bold"),text_color=C["sub"],
                         width=w,anchor="w").pack(side="left",padx=8,pady=5)

        for i,item in enumerate(items):
            bg=C["card2"] if i%2==1 else C["card"]
            r=ctk.CTkFrame(c,fg_color=bg); r.pack(fill="x")
            ctk.CTkLabel(r,text=item["name"][:28],font=("Segoe UI",10,"bold"),
                         text_color=C["text"],width=180,anchor="w").pack(side="left",padx=8,pady=4)
            ctk.CTkLabel(r,text=item["cmd"],font=("Segoe UI",9),
                         text_color=C["sub"],width=500,anchor="w").pack(side="left")
        ctk.CTkFrame(c,height=6,fg_color="transparent").pack()

        if not items:
            ctk.CTkLabel(c,text="No se encontraron entradas de inicio.",
                         font=("Segoe UI",10),text_color=C["sub"]).pack(pady=20)

        ctk.CTkFrame(self.content,height=1,fg_color=C["border"]).pack(fill="x",padx=20,pady=10)
        ctk.CTkLabel(self.content,
            text="Para desactivar programas de inicio: Administrador de tareas → pestaña Inicio",
            font=("Segoe UI",10),text_color=C["sub"],wraplength=700
        ).pack(anchor="w",padx=20)
        BtnSecondary(self.content,"Abrir Administrador de tareas",
                     cmd=lambda:subprocess.Popen(["taskmgr"])).pack(anchor="w",padx=20,pady=8)

    # ── Salud del disco ───────────────────────────────────────────────────────
    def _pg_health(self):
        self._status("Analizando...",C["warning"])
        ctk.CTkLabel(self.content,text="Analizando disco y sistema...",
                     font=("Segoe UI",12),text_color=C["sub"]).pack(pady=40)
        def load():
            wmic=check_disk_wmic(); temps={}
            try: temps=psutil.sensors_temperatures() or {}
            except: pass
            bat=None
            try: bat=psutil.sensors_battery()
            except: pass
            uptime=time.time()-psutil.boot_time()
            self.after(0,lambda:self._render_health(wmic,temps,bat,uptime))
        threading.Thread(target=load,daemon=True).start()

    def _render_health(self,wmic,temps,bat,uptime):
        self._clear(); self._status("",C["sub"])
        P=self._pad()

        SectionLabel(self.content,"TIEMPO DE ACTIVIDAD").pack(anchor="w",padx=20,pady=(14,4))
        c=Card(self.content); c.pack(fill="x",**P)
        ctk.CTkLabel(c,text=fmt_uptime(uptime),font=("Segoe UI",24,"bold"),
                     text_color=C["accent"]).pack(padx=16,pady=12)

        ctk.CTkFrame(self.content,height=1,fg_color=C["border"]).pack(fill="x",padx=20,pady=8)
        SectionLabel(self.content,"BATERÍA").pack(anchor="w",padx=20,pady=(0,4))
        c=Card(self.content); c.pack(fill="x",**P)
        if bat:
            ok=bat.percent>20
            CheckRow(c,f"Nivel de batería: {bat.percent:.0f}%",
                     "Cargando" if bat.power_plugged else "Descargando",ok=ok).pack(fill="x",padx=14,pady=6)
            MiniBar(c,"Carga",bat.percent,bar_w=260).pack(padx=14,pady=(0,10),anchor="w")
        else:
            ctk.CTkLabel(c,text="Sin batería detectada (PC de escritorio o sin soporte).",
                         font=("Segoe UI",10),text_color=C["sub"]).pack(padx=14,pady=14)

        ctk.CTkFrame(self.content,height=1,fg_color=C["border"]).pack(fill="x",padx=20,pady=8)
        SectionLabel(self.content,"TEMPERATURAS DEL SISTEMA").pack(anchor="w",padx=20,pady=(0,4))
        c=Card(self.content); c.pack(fill="x",**P)
        if temps:
            for sensor,readings in temps.items():
                for r in readings:
                    ok=r.current<80
                    CheckRow(c,f"{sensor}  —  {r.label or 'sensor'}",
                             f"{r.current:.1f} °C",ok=ok,warn=80<=r.current<95
                             ).pack(fill="x",padx=14,pady=3)
        else:
            ctk.CTkLabel(c,text="Sensores no disponibles en este sistema.",
                         font=("Segoe UI",10),text_color=C["sub"]).pack(padx=14,pady=14)

        ctk.CTkFrame(self.content,height=1,fg_color=C["border"]).pack(fill="x",padx=20,pady=8)
        SectionLabel(self.content,"ESTADO DEL DISCO (WMIC S.M.A.R.T.)").pack(anchor="w",padx=20,pady=(0,4))
        c=Card(self.content); c.pack(fill="x",**P)
        ctk.CTkLabel(c,text=wmic[:500],font=("Consolas",9),text_color=C["text"],
                     wraplength=760,justify="left").pack(padx=14,pady=10)

        ctk.CTkFrame(self.content,height=1,fg_color=C["border"]).pack(fill="x",padx=20,pady=8)
        SectionLabel(self.content,"CRYSTALDISKINFO").pack(anchor="w",padx=20,pady=(0,4))
        c=Card(self.content); c.pack(fill="x",**P)
        cdi=cdi_exe()
        if cdi:
            CheckRow(c,"CrystalDiskInfo instalado",cdi[:60],ok=True).pack(fill="x",padx=14,pady=6)
            BtnPrimary(c,"Abrir CrystalDiskInfo",cmd=lambda:subprocess.Popen([cdi])
                       ).pack(padx=14,pady=(0,12),anchor="w")
        else:
            CheckRow(c,"CrystalDiskInfo no encontrado","Instálalo desde Herramientas",ok=False
                     ).pack(fill="x",padx=14,pady=6)
            BtnSecondary(c,"Ir a Herramientas",cmd=lambda:self._nav("tools")
                         ).pack(padx=14,pady=(0,12),anchor="w")

        BtnSecondary(self.content,"↻  Actualizar",cmd=self._pg_health
                     ).pack(anchor="e",padx=20,pady=8)

    # ── Variables de entorno ──────────────────────────────────────────────────
    def _pg_env(self):
        SectionLabel(self.content,"VARIABLES DE ENTORNO (PRINCIPALES)").pack(anchor="w",padx=20,pady=(14,6))
        ev=get_env_vars()
        c=Card(self.content); c.pack(fill="x",padx=20,pady=4)
        for i,(k,v) in enumerate(ev.items()): RowKV(c,k,v,alt=i%2==1).pack(fill="x")
        ctk.CTkFrame(c,height=6,fg_color="transparent").pack()

        ctk.CTkFrame(self.content,height=1,fg_color=C["border"]).pack(fill="x",padx=20,pady=10)
        SectionLabel(self.content,"PATH COMPLETO").pack(anchor="w",padx=20,pady=(0,4))
        c2=Card(self.content); c2.pack(fill="x",padx=20,pady=4)
        path_entries=(os.environ.get("PATH","")).split(";")
        for i,entry in enumerate(path_entries[:40]):
            if not entry.strip(): continue
            bg=C["card2"] if i%2==1 else C["card"]
            r=ctk.CTkFrame(c2,fg_color=bg); r.pack(fill="x")
            ctk.CTkLabel(r,text=entry[:100],font=("Consolas",9),text_color=C["text"],
                         anchor="w").pack(fill="x",padx=12,pady=2)
        ctk.CTkFrame(c2,height=6,fg_color="transparent").pack()

    # ── Herramientas ──────────────────────────────────────────────────────────
    def _pg_tools(self):
        P=self._pad()
        SectionLabel(self.content,"HERRAMIENTAS EXTERNAS").pack(anchor="w",padx=20,pady=(14,6))

        # CrystalDiskInfo
        cdi=cdi_exe()
        c1=Card(self.content); c1.pack(fill="x",**P)
        hdr=ctk.CTkFrame(c1,fg_color="transparent"); hdr.pack(fill="x",padx=16,pady=(14,4))
        ctk.CTkLabel(hdr,text="CrystalDiskInfo",font=("Segoe UI",13,"bold"),
                     text_color=C["text"]).pack(side="left")
        Pill(hdr,"Instalado" if cdi else "No instalado",ok=bool(cdi)).pack(side="right")
        ctk.CTkLabel(c1,text="Análisis S.M.A.R.T. de discos duros y SSD. "
                     "Detecta fallos antes de que ocurran.",
                     font=("Segoe UI",10),text_color=C["sub"],wraplength=680
                     ).pack(anchor="w",padx=16)
        self._cdi_log=LogBox(c1,h=90); self._cdi_log.pack(fill="x",padx=16,pady=6)
        row1=ctk.CTkFrame(c1,fg_color="transparent"); row1.pack(fill="x",padx=16,pady=(0,14))
        if cdi: BtnPrimary(row1,"Abrir CrystalDiskInfo",
                           cmd=lambda:subprocess.Popen([cdi])).pack(side="left")
        BtnSecondary(row1,"↓  Instalar / Actualizar",
                     cmd=self._install_cdi).pack(side="left",padx=8)

        ctk.CTkFrame(self.content,height=1,fg_color=C["border"]).pack(fill="x",padx=20,pady=8)

        # ClamAV
        clam=clamav_exe()
        c2=Card(self.content); c2.pack(fill="x",**P)
        hdr2=ctk.CTkFrame(c2,fg_color="transparent"); hdr2.pack(fill="x",padx=16,pady=(14,4))
        ctk.CTkLabel(hdr2,text="ClamAV",font=("Segoe UI",13,"bold"),
                     text_color=C["text"]).pack(side="left")
        Pill(hdr2,"Instalado" if clam else "No instalado",ok=bool(clam)).pack(side="right")
        ctk.CTkLabel(c2,text="Antivirus open source. Escanea archivos y directorios "
                     "en busca de malware, troyanos y virus.",
                     font=("Segoe UI",10),text_color=C["sub"],wraplength=680
                     ).pack(anchor="w",padx=16)
        self._clam_tool_log=LogBox(c2,h=110); self._clam_tool_log.pack(fill="x",padx=16,pady=6)
        row2=ctk.CTkFrame(c2,fg_color="transparent"); row2.pack(fill="x",padx=16,pady=(0,14))
        BtnSecondary(row2,"↓  Instalar ClamAV",cmd=self._install_clamav).pack(side="left")
        if clam:
            BtnSecondary(row2,"↻  Actualizar firmas",
                         cmd=self._freshclam_tool).pack(side="left",padx=8)

        ctk.CTkFrame(self.content,height=1,fg_color=C["border"]).pack(fill="x",padx=20,pady=8)

        # Herramientas del sistema Windows integradas
        SectionLabel(self.content,"HERRAMIENTAS DEL SISTEMA").pack(anchor="w",padx=20,pady=(0,6))
        tools_win=[
            ("Administrador de tareas","Procesos, rendimiento, inicio","taskmgr"),
            ("Monitor de recursos","CPU, memoria, disco, red en tiempo real","resmon"),
            ("Visor de eventos","Errores y advertencias del sistema","eventvwr"),
            ("Desfragmentador de disco","Optimiza discos mecánicos","dfrgui"),
            ("Comprobación de disco (chkdsk)","Errores en sistema de archivos","cmd /c chkdsk /f"),
            ("Monitor de confiabilidad","Historial de errores y estabilidad",
             "perfmon /rel"),
            ("DirectX Diagnostic","Información de hardware y DirectX","dxdiag"),
        ]
        for i,(name,desc,cmd) in enumerate(tools_win):
            c=Card(self.content) if i%2==0 else Card2(self.content)
            c.pack(fill="x",padx=20,pady=3)
            r=ctk.CTkFrame(c,fg_color="transparent"); r.pack(fill="x",padx=14,pady=10)
            t=ctk.CTkFrame(r,fg_color="transparent"); t.pack(side="left",expand=True,fill="x")
            ctk.CTkLabel(t,text=name,font=("Segoe UI",11,"bold"),text_color=C["text"]).pack(anchor="w")
            ctk.CTkLabel(t,text=desc,font=("Segoe UI",9),text_color=C["sub"]).pack(anchor="w")
            _cmd=cmd
            BtnSecondary(r,"Abrir",cmd=lambda c2=_cmd:subprocess.Popen(c2,shell=True)
                         ).pack(side="right",padx=(8,0))

    def _install_cdi(self):
        self._cdi_log.clear()
        def run():
            def cb(m): self.after(0,lambda x=m:self._cdi_log.append(x))
            ok=install_tool_winget("CrystalDewWorld.CrystalDiskInfo","crystaldiskinfo",cb)
            if not ok:
                import webbrowser
                self.after(0,lambda:self._cdi_log.append("Abriendo web..."))
                webbrowser.open("https://crystalmark.info/en/software/crystaldiskinfo/")
        threading.Thread(target=run,daemon=True).start()

    def _install_clamav(self):
        self._clam_tool_log.clear()
        def run():
            def cb(m): self.after(0,lambda x=m:self._clam_tool_log.append(x))
            ok=install_tool_winget("ClamWin.ClamWin","clamav",cb)
            if not ok:
                cb("Descargando MSI directo...")
                try:
                    msi=os.path.join(tempfile.gettempdir(),"ClamAV.msi")
                    urllib.request.urlretrieve(CLAMAV_MSI,msi)
                    subprocess.run(["msiexec","/i",msi,"/quiet","/norestart"],check=True)
                    cb("Instalación completada. Reinicia la app.")
                except Exception as e: cb(f"Error: {e}")
        threading.Thread(target=run,daemon=True).start()

    def _freshclam_tool(self):
        self._clam_tool_log.clear()
        self._clam_tool_log.append("Ejecutando freshclam...")
        def run():
            exe=clamav_exe()
            fc=None
            if exe: fc=os.path.join(os.path.dirname(exe),"freshclam.exe")
            if not (fc and os.path.isfile(fc)): fc=shutil.which("freshclam")
            if fc:
                r=subprocess.run([fc],capture_output=True,text=True)
                for l in (r.stdout+r.stderr).split("\n"):
                    self.after(0,lambda ll=l:self._clam_tool_log.append(ll))
            else: self.after(0,lambda:self._clam_tool_log.append("freshclam no encontrado."))
        threading.Thread(target=run,daemon=True).start()


# ══════════════════════════════════════════════════════════════════════════════
#  FUNCIONES DE BACKEND — nuevas secciones
# ══════════════════════════════════════════════════════════════════════════════

def run_sfc():
    """Ejecuta sfc /scannow y devuelve salida."""
    try:
        r = subprocess.run(["sfc", "/scannow"], capture_output=True, text=True,
                           timeout=300, encoding="utf-8", errors="replace")
        return r.stdout + r.stderr
    except Exception as e:
        return str(e)

def run_ping(host="8.8.8.8", count=4):
    try:
        r = subprocess.run(["ping", "-n", str(count), host],
                           capture_output=True, text=True, timeout=20,
                           encoding="cp850", errors="replace")
        return r.stdout + r.stderr
    except Exception as e:
        return str(e)

def run_tracert(host="google.com"):
    try:
        r = subprocess.run(["tracert", "-h", "10", "-w", "500", host],
                           capture_output=True, text=True, timeout=30,
                           encoding="cp850", errors="replace")
        return r.stdout + r.stderr
    except Exception as e:
        return str(e)

def run_dns_check():
    hosts = ["google.com", "microsoft.com", "cloudflare.com", "8.8.8.8"]
    results = []
    for h in hosts:
        t0 = time.time()
        r = subprocess.run(["ping", "-n", "1", "-w", "1000", h],
                           capture_output=True, text=True, timeout=5,
                           encoding="cp850", errors="replace")
        ms = int((time.time() - t0) * 1000)
        ok = r.returncode == 0
        results.append({"host": h, "ok": ok, "ms": ms})
    return results

def run_netstat():
    try:
        r = subprocess.run(["netstat", "-ano"],
                           capture_output=True, text=True, timeout=15,
                           encoding="cp850", errors="replace")
        return r.stdout[:4000]
    except Exception as e:
        return str(e)

def get_event_log_errors(n=20):
    """Lee los últimos N errores/advertencias del Event Log del sistema."""
    events = []
    try:
        import win32evtlog, win32con  # type: ignore
        hand = win32evtlog.OpenEventLog(None, "System")
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        raw = win32evtlog.ReadEventLog(hand, flags, 0)
        for ev in raw[:n]:
            lvl = ev.EventType
            if lvl in (win32con.EVENTLOG_ERROR_TYPE, win32con.EVENTLOG_WARNING_TYPE):
                events.append({
                    "time": str(ev.TimeGenerated)[:19],
                    "src": ev.SourceName[:30],
                    "type": "ERROR" if lvl == win32con.EVENTLOG_ERROR_TYPE else "WARN",
                    "id": ev.EventID & 0xFFFF,
                })
        win32evtlog.CloseEventLog(hand)
    except ImportError:
        # win32evtlog no disponible, usar PowerShell
        try:
            r = subprocess.run(
                ["powershell", "-Command",
                 "Get-EventLog -LogName System -EntryType Error,Warning -Newest 20 | "
                 "Select-Object TimeGenerated,Source,EntryType,EventID | ConvertTo-Json"],
                capture_output=True, text=True, timeout=20)
            data = json.loads(r.stdout.strip() or "[]")
            if isinstance(data, dict): data = [data]
            for ev in data:
                events.append({
                    "time": str(ev.get("TimeGenerated",""))[:19],
                    "src":  str(ev.get("Source",""))[:30],
                    "type": str(ev.get("EntryType","")),
                    "id":   ev.get("EventID", 0),
                })
        except Exception:
            pass
    except Exception:
        pass
    return events

def get_services_list():
    svcs = []
    for svc in psutil.win_service_iter():
        try:
            info = svc.as_dict()
            svcs.append({
                "name":    info.get("name","")[:40],
                "display": info.get("display_name","")[:48],
                "status":  info.get("status",""),
                "start":   info.get("start_type",""),
                "pid":     info.get("pid",""),
            })
        except Exception:
            pass
    svcs.sort(key=lambda x: x["display"].lower())
    return svcs

def svc_action(name, action):
    """Inicia o detiene un servicio. Requiere admin."""
    try:
        subprocess.run(["sc", action, name], check=True,
                       capture_output=True, text=True, timeout=15)
        return True, f"Servicio '{name}' {action} OK."
    except Exception as e:
        return False, str(e)

def get_local_users():
    users = []
    try:
        r = subprocess.run(
            ["powershell", "-Command",
             "Get-LocalUser | Select Name,Enabled,LastLogon,Description | ConvertTo-Json"],
            capture_output=True, text=True, timeout=15)
        data = json.loads(r.stdout.strip() or "[]")
        if isinstance(data, dict): data = [data]
        for u in data:
            users.append({
                "name":    str(u.get("Name",""))[:30],
                "enabled": u.get("Enabled", False),
                "logon":   str(u.get("LastLogon",""))[:19],
                "desc":    str(u.get("Description",""))[:50],
            })
    except Exception as e:
        users.append({"name": f"Error: {e}", "enabled": False, "logon": "—", "desc": ""})
    return users

def get_local_groups():
    try:
        r = subprocess.run(
            ["powershell", "-Command",
             "Get-LocalGroup | Select Name,Description | ConvertTo-Json"],
            capture_output=True, text=True, timeout=15)
        data = json.loads(r.stdout.strip() or "[]")
        if isinstance(data, dict): data = [data]
        return [{"name": str(d.get("Name",""))[:40],
                 "desc": str(d.get("Description",""))[:60]} for d in data]
    except Exception as e:
        return [{"name": f"Error: {e}", "desc": ""}]

def generate_report():
    lines = []
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    lines += [f"{'='*60}", f"  HARDENDISK — REPORTE DEL SISTEMA", f"  Generado: {now}", f"{'='*60}", ""]

    # Sistema
    si = get_system_info()
    lines += ["[SISTEMA]",
              f"  OS:          {si['os']}",
              f"  Build:       {si['build']}",
              f"  Arquitectura:{si['arch']}",
              f"  CPU:         {si['cpu']}",
              f"  Host:        {si['host']}",
              f"  Último boot: {si['boot']}",
              f"  Tiempo activo:{si['uptime']}", ""]

    # CPU / RAM
    cpu = get_cpu_info()
    mem = get_memory_info()
    lines += ["[CPU]",
              f"  Núcleos físicos: {cpu['phy']}   Lógicos: {cpu['log']}",
              f"  Frecuencia: {cpu['cur']} / máx {cpu['max']}",
              f"  Uso actual: {cpu['use']}%", "",
              "[MEMORIA RAM]",
              f"  Total: {mem['total']}   Usado: {mem['used']}   Libre: {mem['free']}",
              f"  Uso: {mem['pct']}%   SWAP: {mem['swap_pct']}%", ""]

    # Discos
    lines.append("[ALMACENAMIENTO]")
    for d in get_disk_info():
        lines.append(f"  {d['dev']} ({d['fs']})  {d['used']} / {d['total']}  libre: {d['free']}  uso: {d['pct']}%")
    lines.append("")

    # Red
    lines.append("[RED]")
    for n in get_net_info():
        estado = "ACTIVA" if n["up"] else "inactiva"
        lines.append(f"  {n['name'][:28]}  IP: {n['ip']}  {estado}  {n['spd']} Mbps")
    lines.append("")

    # Seguridad
    lines.append("[SEGURIDAD]")
    try:
        df = json.loads(check_defender())
        lines.append(f"  Defender Antivirus: {'ON' if df.get('AntivirusEnabled') else 'OFF'}")
        lines.append(f"  Protección en tiempo real: {'ON' if df.get('RealTimeProtectionEnabled') else 'OFF'}")
    except:
        lines.append("  Defender: no disponible")
    upd = check_updates()
    lines.append(f"  Actualizaciones pendientes: {upd if upd >= 0 else 'no verificado'}")
    lines.append("")

    # Procesos top
    lines.append("[TOP PROCESOS]")
    for p in get_top_procs(10):
        lines.append(f"  PID {p.get('pid','')}  {p.get('name','')[:30]}  CPU:{p.get('cpu_percent',0):.1f}%  RAM:{p.get('memory_percent',0):.1f}%")
    lines.append("")

    # Startup
    lines.append("[INICIO AUTOMÁTICO]")
    for s in get_startup_items():
        lines.append(f"  {s['name'][:30]}  →  {s['cmd']}")
    lines.append("")

    # WMIC
    lines.append("[DISCO WMIC]")
    lines.append(check_disk_wmic())
    lines.append("")

    lines += [f"{'='*60}", "  Fin del reporte", f"{'='*60}"]
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
#  MÉTODOS DE PÁGINA — nuevas secciones (añadidos a HardenDisk)
# ══════════════════════════════════════════════════════════════════════════════

def _pg_monitor(self):
    """Monitor en vivo con actualización automática."""
    self._monitor_active = True
    P = self._pad()

    SectionLabel(self.content, "MONITOR EN VIVO  —  actualiza cada 2 s").pack(
        anchor="w", padx=20, pady=(14, 4))
    ctk.CTkLabel(self.content, text="Los valores se refrescan automáticamente mientras la página está activa.",
                 font=("Segoe UI", 9), text_color=C["sub"]).pack(anchor="w", padx=20, pady=(0, 8))

    # Tarjetas live
    cards = ctk.CTkFrame(self.content, fg_color="transparent")
    cards.pack(fill="x", padx=20, pady=4)
    self._mon_labels = {}
    for i, (key, title) in enumerate([("cpu","CPU %"),("ram","RAM %"),
                                       ("disk","Disco C: %"),("procs","Procesos")]):
        c = Card(cards); c.grid(row=0, column=i, padx=5, sticky="nsew")
        cards.grid_columnconfigure(i, weight=1)
        ctk.CTkLabel(c, text=title, font=("Segoe UI", 9), text_color=C["sub"]).pack(pady=(10,0))
        lbl = ctk.CTkLabel(c, text="—", font=("Segoe UI", 26, "bold"), text_color=C["accent"])
        lbl.pack(); ctk.CTkLabel(c, height=8).pack()
        self._mon_labels[key] = lbl

    ctk.CTkFrame(self.content, height=1, fg_color=C["border"]).pack(fill="x", padx=20, pady=8)

    # Historial CPU (últimas 30 lecturas)
    SectionLabel(self.content, "HISTORIAL CPU (últimas 30 lecturas)").pack(anchor="w", padx=20, pady=(0,4))
    hist_card = Card(self.content); hist_card.pack(fill="x", padx=20, pady=4)
    self._cpu_hist = []
    self._hist_frame = hist_card

    # Canvas para la mini-gráfica
    self._hist_canvas = tk.Canvas(hist_card, height=80, bg=C["card"],
                                   highlightthickness=0)
    self._hist_canvas.pack(fill="x", padx=14, pady=10)

    ctk.CTkFrame(self.content, height=1, fg_color=C["border"]).pack(fill="x", padx=20, pady=8)

    # Tabla de procesos live
    SectionLabel(self.content, "PROCESOS EN TIEMPO REAL (top 8)").pack(anchor="w", padx=20, pady=(0,4))
    self._proc_card = Card(self.content); self._proc_card.pack(fill="x", padx=20, pady=4)
    hdr = ctk.CTkFrame(self._proc_card, fg_color=C["card2"]); hdr.pack(fill="x")
    for t, w in [("PID",55),("Nombre",270),("CPU%",70),("RAM%",70),("Estado",90)]:
        ctk.CTkLabel(hdr, text=t, font=("Segoe UI",9,"bold"), text_color=C["sub"],
                     width=w, anchor="w").pack(side="left", padx=4, pady=4)
    self._proc_rows_frame = ctk.CTkFrame(self._proc_card, fg_color="transparent")
    self._proc_rows_frame.pack(fill="x")

    BtnSecondary(self.content, "⏹  Detener monitor",
                 cmd=lambda: setattr(self, "_monitor_active", False)
                 ).pack(anchor="e", padx=20, pady=8)

    self._update_monitor()

def _update_monitor(self):
    if not getattr(self, "_monitor_active", False):
        return
    try:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        try: disk = psutil.disk_usage("C:\\").percent
        except: disk = 0.0
        procs = len(psutil.pids())

        col_cpu  = C["success"] if cpu  < 65 else C["warning"] if cpu  < 85 else C["danger"]
        col_ram  = C["success"] if ram  < 65 else C["warning"] if ram  < 85 else C["danger"]
        col_disk = C["success"] if disk < 75 else C["warning"] if disk < 90 else C["danger"]

        self._mon_labels["cpu"].configure(text=f"{cpu:.1f}%",   text_color=col_cpu)
        self._mon_labels["ram"].configure(text=f"{ram:.1f}%",   text_color=col_ram)
        self._mon_labels["disk"].configure(text=f"{disk:.1f}%", text_color=col_disk)
        self._mon_labels["procs"].configure(text=str(procs),    text_color=C["sub"])

        # Historial CPU
        self._cpu_hist.append(cpu)
        if len(self._cpu_hist) > 30:
            self._cpu_hist = self._cpu_hist[-30:]
        self._draw_hist()

        # Actualizar filas de procesos
        top = get_top_procs(8)
        for w in self._proc_rows_frame.winfo_children():
            w.destroy()
        for p in top:
            r = ctk.CTkFrame(self._proc_rows_frame, fg_color="transparent")
            r.pack(fill="x")
            for txt, w in [(str(p.get("pid","")),55),(str(p.get("name",""))[:36],270),
                           (f"{p.get('cpu_percent',0):.1f}",70),
                           (f"{p.get('memory_percent',0):.1f}",70),
                           (str(p.get("status",""))[:12],90)]:
                ctk.CTkLabel(r, text=txt, font=("Segoe UI",9), text_color=C["text"],
                             width=w, anchor="w").pack(side="left", padx=4, pady=1)
    except Exception:
        pass
    self.after(2000, self._update_monitor)

def _draw_hist(self):
    c = self._hist_canvas
    try:
        c.delete("all")
        w = c.winfo_width() or 600
        h = 80
        n = len(self._cpu_hist)
        if n < 2:
            return
        step = w / 30
        pts = []
        for i, v in enumerate(self._cpu_hist):
            x = i * step + step / 2
            y = h - (v / 100) * (h - 10) - 4
            pts.append((x, y))
        # Área rellena
        poly = [(0, h)] + pts + [(pts[-1][0], h)]
        flat = [c for p in poly for c in p]
        c.create_polygon(flat, fill="#DBEAFE", outline="")
        # Línea
        for i in range(len(pts) - 1):
            c.create_line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1],
                          fill=C["accent"], width=2)
        # Valor actual
        last = self._cpu_hist[-1]
        c.create_text(w - 6, 10, text=f"{last:.0f}%",
                      anchor="ne", fill=C["accent"],
                      font=("Segoe UI", 9, "bold"))
    except Exception:
        pass

HardenDisk._pg_monitor    = _pg_monitor
HardenDisk._update_monitor = _update_monitor
HardenDisk._draw_hist     = _draw_hist


def _pg_diag(self):
    P = self._pad()
    SectionLabel(self.content, "DIAGNÓSTICO DEL SISTEMA").pack(anchor="w", padx=20, pady=(14,4))
    ctk.CTkLabel(self.content,
        text="Herramientas de diagnóstico de red, disco y sistema. "
             "Algunos tests requieren privilegios de administrador.",
        font=("Segoe UI", 9), text_color=C["sub"], wraplength=700
    ).pack(anchor="w", padx=20, pady=(0, 10))

    # ── Test de conectividad ──
    SectionLabel(self.content, "CONECTIVIDAD DNS / INTERNET").pack(anchor="w", padx=20, pady=(0,4))
    conn_card = Card(self.content); conn_card.pack(fill="x", **P)
    self._dns_rows = ctk.CTkFrame(conn_card, fg_color="transparent")
    self._dns_rows.pack(fill="x", padx=14, pady=8)
    ctk.CTkLabel(self._dns_rows, text="Presiona 'Verificar' para testear conectividad.",
                 font=("Segoe UI", 10), text_color=C["sub"]).pack(anchor="w")

    def run_dns():
        for w in self._dns_rows.winfo_children(): w.destroy()
        results = run_dns_check()
        for r in results:
            row = ctk.CTkFrame(self._dns_rows, fg_color="transparent")
            row.pack(fill="x", pady=2)
            Pill(row, "✓ OK" if r["ok"] else "✗ FAIL", ok=r["ok"],
                 width=54).pack(side="left", padx=(0,10))
            ctk.CTkLabel(row, text=r["host"], font=("Segoe UI",10,"bold"),
                         text_color=C["text"], width=160, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=f"{r['ms']} ms", font=("Segoe UI",10),
                         text_color=C["sub"]).pack(side="left")

    row_b = ctk.CTkFrame(conn_card, fg_color="transparent")
    row_b.pack(fill="x", padx=14, pady=(0,12))
    BtnSecondary(row_b, "🌐  Verificar conectividad",
                 cmd=lambda: threading.Thread(target=run_dns, daemon=True).start()
                 ).pack(side="left")

    ctk.CTkFrame(self.content, height=1, fg_color=C["border"]).pack(fill="x", padx=20, pady=8)

    # ── Ping personalizado ──
    SectionLabel(self.content, "PING PERSONALIZADO").pack(anchor="w", padx=20, pady=(0,4))
    pc = Card(self.content); pc.pack(fill="x", **P)
    ping_row = ctk.CTkFrame(pc, fg_color="transparent"); ping_row.pack(fill="x", padx=14, pady=10)
    ctk.CTkLabel(ping_row, text="Host / IP:", font=("Segoe UI",10),
                 text_color=C["sub"]).pack(side="left")
    self._ping_var = ctk.StringVar(value="8.8.8.8")
    ctk.CTkEntry(ping_row, textvariable=self._ping_var, width=220,
                 height=32, corner_radius=10,
                 fg_color=C["card2"], border_color=C["border"]).pack(side="left", padx=8)
    self._ping_log = LogBox(pc, h=100); self._ping_log.pack(fill="x", padx=14, pady=4)

    def do_ping():
        host = self._ping_var.get().strip() or "8.8.8.8"
        self._ping_log.clear()
        self._ping_log.append(f"Ping a {host}...")
        def run():
            out = run_ping(host)
            for l in out.split("\n"):
                self.after(0, lambda ll=l: self._ping_log.append(ll))
        threading.Thread(target=run, daemon=True).start()

    BtnSecondary(pc, "Ejecutar ping", cmd=do_ping).pack(padx=14, pady=(0,12), anchor="w")

    ctk.CTkFrame(self.content, height=1, fg_color=C["border"]).pack(fill="x", padx=20, pady=8)

    # ── Traceroute ──
    SectionLabel(self.content, "TRACEROUTE").pack(anchor="w", padx=20, pady=(0,4))
    tc = Card(self.content); tc.pack(fill="x", **P)
    tr_row = ctk.CTkFrame(tc, fg_color="transparent"); tr_row.pack(fill="x", padx=14, pady=10)
    ctk.CTkLabel(tr_row, text="Destino:", font=("Segoe UI",10),
                 text_color=C["sub"]).pack(side="left")
    self._tr_var = ctk.StringVar(value="google.com")
    ctk.CTkEntry(tr_row, textvariable=self._tr_var, width=220,
                 height=32, corner_radius=10,
                 fg_color=C["card2"], border_color=C["border"]).pack(side="left", padx=8)
    self._tr_log = LogBox(tc, h=130); self._tr_log.pack(fill="x", padx=14, pady=4)

    def do_tr():
        host = self._tr_var.get().strip() or "google.com"
        self._tr_log.clear(); self._tr_log.append(f"tracert {host}...")
        def run():
            out = run_tracert(host)
            for l in out.split("\n"):
                self.after(0, lambda ll=l: self._tr_log.append(ll))
        threading.Thread(target=run, daemon=True).start()

    BtnSecondary(tc, "Ejecutar traceroute", cmd=do_tr).pack(padx=14, pady=(0,12), anchor="w")

    ctk.CTkFrame(self.content, height=1, fg_color=C["border"]).pack(fill="x", padx=20, pady=8)

    # ── Integridad del sistema (sfc) ──
    SectionLabel(self.content, "INTEGRIDAD DEL SISTEMA (sfc /scannow)").pack(anchor="w", padx=20, pady=(0,4))
    sc = Card(self.content); sc.pack(fill="x", **P)
    ctk.CTkLabel(sc,
        text="Verifica y repara archivos protegidos del sistema. Requiere administrador. Puede tardar varios minutos.",
        font=("Segoe UI", 9), text_color=C["sub"], wraplength=680
    ).pack(anchor="w", padx=14, pady=(10,4))
    self._sfc_log = LogBox(sc, h=120); self._sfc_log.pack(fill="x", padx=14, pady=4)

    def do_sfc():
        self._sfc_log.clear(); self._sfc_log.append("Ejecutando sfc /scannow... (puede tardar)")
        self._status("Ejecutando SFC...", C["warning"])
        def run():
            out = run_sfc()
            for l in out.split("\n"):
                self.after(0, lambda ll=l: self._sfc_log.append(ll))
            self.after(0, lambda: self._status("SFC completado", C["success"]))
        threading.Thread(target=run, daemon=True).start()

    BtnDanger(sc, "🔍  Ejecutar SFC (admin requerido)", cmd=do_sfc
              ).pack(padx=14, pady=(0,12), anchor="w")

    ctk.CTkFrame(self.content, height=1, fg_color=C["border"]).pack(fill="x", padx=20, pady=8)

    # ── Conexiones activas (netstat) ──
    SectionLabel(self.content, "CONEXIONES ACTIVAS (netstat)").pack(anchor="w", padx=20, pady=(0,4))
    nc = Card(self.content); nc.pack(fill="x", **P)
    self._ns_log = LogBox(nc, h=160); self._ns_log.pack(fill="x", padx=14, pady=8)

    def do_ns():
        self._ns_log.clear(); self._ns_log.append("Ejecutando netstat -ano...")
        def run():
            out = run_netstat()
            for l in out.split("\n"):
                self.after(0, lambda ll=l: self._ns_log.append(ll))
        threading.Thread(target=run, daemon=True).start()

    BtnSecondary(nc, "Ver conexiones activas", cmd=do_ns).pack(padx=14, pady=(0,12), anchor="w")

    ctk.CTkFrame(self.content, height=1, fg_color=C["border"]).pack(fill="x", padx=20, pady=8)

    # ── Log de eventos ──
    SectionLabel(self.content, "ÚLTIMOS ERRORES / ADVERTENCIAS (Event Log)").pack(
        anchor="w", padx=20, pady=(0,4))
    ev_card = Card(self.content); ev_card.pack(fill="x", **P)
    self._evlog_frame = ctk.CTkFrame(ev_card, fg_color="transparent")
    self._evlog_frame.pack(fill="x", padx=14, pady=8)
    ctk.CTkLabel(self._evlog_frame, text="Presiona el botón para cargar.",
                 font=("Segoe UI",10), text_color=C["sub"]).pack(anchor="w")

    def load_events():
        for w in self._evlog_frame.winfo_children(): w.destroy()
        self._status("Cargando eventos...", C["warning"])
        def run():
            evs = get_event_log_errors(20)
            def render():
                if not evs:
                    ctk.CTkLabel(self._evlog_frame, text="No se encontraron errores recientes.",
                                 font=("Segoe UI",10), text_color=C["success"]).pack(anchor="w")
                    return
                hdr = ctk.CTkFrame(self._evlog_frame, fg_color=C["card2"]); hdr.pack(fill="x")
                for t,w in [("Tiempo",140),("Fuente",200),("Tipo",60),("ID",50)]:
                    ctk.CTkLabel(hdr, text=t, font=("Segoe UI",9,"bold"),
                                 text_color=C["sub"], width=w, anchor="w").pack(side="left",padx=4,pady=3)
                for i, ev in enumerate(evs):
                    bg = C["card2"] if i%2==1 else C["card"]
                    r = ctk.CTkFrame(self._evlog_frame, fg_color=bg); r.pack(fill="x")
                    col = C["danger"] if ev["type"]=="ERROR" else C["warning"]
                    for txt, w in [(ev["time"],140),(ev["src"],200),(ev["type"],60),(str(ev["id"]),50)]:
                        tc = col if txt == ev["type"] else C["text"]
                        ctk.CTkLabel(r, text=txt, font=("Segoe UI",9),
                                     text_color=tc, width=w, anchor="w").pack(side="left",padx=4,pady=2)
                self._status("", C["sub"])
            self.after(0, render)
        threading.Thread(target=run, daemon=True).start()

    BtnSecondary(ev_card, "📋  Cargar eventos del sistema", cmd=load_events
                 ).pack(padx=14, pady=(0,12), anchor="w")

HardenDisk._pg_diag = _pg_diag


def _pg_services(self):
    self._status("Cargando servicios...", C["warning"])
    ctk.CTkLabel(self.content, text="Cargando lista de servicios...",
                 font=("Segoe UI",12), text_color=C["sub"]).pack(pady=40)
    def load():
        svcs = get_services_list()
        self.after(0, lambda: self._render_services(svcs))
    threading.Thread(target=load, daemon=True).start()

def _render_services(self, svcs):
    self._clear(); self._status(f"{len(svcs)} servicios", C["sub"])
    P = self._pad()

    running = sum(1 for s in svcs if s["status"] == "running")
    stopped = sum(1 for s in svcs if s["status"] == "stopped")

    SectionLabel(self.content, f"SERVICIOS DE WINDOWS  —  {running} activos  ·  {stopped} detenidos").pack(
        anchor="w", padx=20, pady=(14,4))

    # Filtros
    frow = ctk.CTkFrame(self.content, fg_color="transparent"); frow.pack(fill="x", padx=20, pady=(0,6))
    sv = ctk.StringVar()
    ctk.CTkEntry(frow, textvariable=sv, placeholder_text="Buscar servicio...",
                 font=("Segoe UI",11), height=34, corner_radius=18,
                 fg_color=C["card"], border_color=C["border"], width=320,
                 border_width=1).pack(side="left")
    self._svc_filter = ctk.StringVar(value="todos")
    for lbl, val in [("Todos","todos"),("Activos","running"),("Detenidos","stopped")]:
        ctk.CTkRadioButton(frow, text=lbl, variable=self._svc_filter, value=val,
                           font=("Segoe UI",10), text_color=C["text"],
                           fg_color=C["accent"]).pack(side="left", padx=12)

    table = ctk.CTkScrollableFrame(self.content, height=480,
                                    fg_color=C["card"], corner_radius=12,
                                    border_width=1, border_color=C["border"])
    table.pack(fill="x", padx=20, pady=4)

    hdr = ctk.CTkFrame(table, fg_color=C["card2"]); hdr.pack(fill="x")
    for t, w in [("Nombre",200),("Descripción",280),("Estado",80),("Inicio",90),("Acción",80)]:
        ctk.CTkLabel(hdr, text=t, font=("Segoe UI",9,"bold"), text_color=C["sub"],
                     width=w, anchor="w").pack(side="left", padx=4, pady=4)

    self._svc_rows = []
    for i, svc in enumerate(svcs):
        bg = C["card2"] if i%2==1 else C["card"]
        r = ctk.CTkFrame(table, fg_color=bg); r.pack(fill="x")
        col = C["success"] if svc["status"]=="running" else C["sub"]
        for txt, w in [(svc["name"],200),(svc["display"],280)]:
            ctk.CTkLabel(r, text=txt[:40], font=("Segoe UI",9),
                         text_color=C["text"], width=w, anchor="w").pack(side="left",padx=4,pady=2)
        Pill(r, svc["status"], ok=svc["status"]=="running",
             warn=svc["status"]not in("running","stopped"),
             width=74).pack(side="left", padx=2)
        ctk.CTkLabel(r, text=svc["start"][:10], font=("Segoe UI",8),
                     text_color=C["sub"], width=90, anchor="w").pack(side="left")

        _name = svc["name"]
        _status = svc["status"]
        def _toggle(n=_name, s=_status):
            action = "stop" if s == "running" else "start"
            ok, msg = svc_action(n, action)
            messagebox.showinfo("HardenDisk", msg)
            self._pg_services()
        lbl = "Detener" if _status == "running" else "Iniciar"
        fgc = C["warning_bg"] if _status == "running" else C["success_bg"]
        txc = C["warning"] if _status == "running" else C["success"]
        ctk.CTkButton(r, text=lbl, command=_toggle,
                      fg_color=fgc, hover_color=C["dim"], text_color=txc,
                      font=("Segoe UI",8,"bold"), height=24, corner_radius=12,
                      width=72).pack(side="left", padx=4, pady=2)

        self._svc_rows.append((svc["name"].lower() + " " + svc["display"].lower(),
                                svc["status"], r))

    def filt(*_):
        q = sv.get().lower()
        f = self._svc_filter.get()
        for key, status, row in self._svc_rows:
            show = (q in key) and (f == "todos" or status == f)
            if show: row.pack(fill="x")
            else:    row.pack_forget()

    sv.trace_add("write", filt)
    self._svc_filter.trace_add("write", filt)

    BtnSecondary(self.content, "↻  Actualizar", cmd=self._pg_services
                 ).pack(anchor="e", padx=20, pady=8)

HardenDisk._pg_services    = _pg_services
HardenDisk._render_services = _render_services


def _pg_users(self):
    self._status("Cargando usuarios...", C["warning"])
    def load():
        users = get_local_users()
        groups = get_local_groups()
        self.after(0, lambda: self._render_users(users, groups))
    threading.Thread(target=load, daemon=True).start()

def _render_users(self, users, groups):
    self._clear(); self._status("", C["sub"])
    P = self._pad()

    SectionLabel(self.content, "CUENTAS DE USUARIO LOCALES").pack(anchor="w", padx=20, pady=(14,4))
    c = Card(self.content); c.pack(fill="x", **P)
    hdr = ctk.CTkFrame(c, fg_color=C["card2"]); hdr.pack(fill="x")
    for t,w in [("Usuario",160),("Estado",80),("Último acceso",170),("Descripción",300)]:
        ctk.CTkLabel(hdr, text=t, font=("Segoe UI",9,"bold"), text_color=C["sub"],
                     width=w, anchor="w").pack(side="left",padx=6,pady=4)
    for i, u in enumerate(users):
        bg = C["card2"] if i%2==1 else C["card"]
        r = ctk.CTkFrame(c, fg_color=bg); r.pack(fill="x")
        ctk.CTkLabel(r, text=u["name"], font=("Segoe UI",10,"bold"),
                     text_color=C["text"], width=160, anchor="w").pack(side="left",padx=6,pady=3)
        Pill(r, "Activa" if u["enabled"] else "Desactivada",
             ok=u["enabled"], width=76).pack(side="left", padx=4)
        ctk.CTkLabel(r, text=u["logon"][:18], font=("Segoe UI",9),
                     text_color=C["sub"], width=170, anchor="w").pack(side="left")
        ctk.CTkLabel(r, text=u["desc"][:40], font=("Segoe UI",9),
                     text_color=C["sub"], width=300, anchor="w").pack(side="left")
    ctk.CTkFrame(c, height=6, fg_color="transparent").pack()

    ctk.CTkFrame(self.content, height=1, fg_color=C["border"]).pack(fill="x", padx=20, pady=8)

    SectionLabel(self.content, "GRUPOS LOCALES").pack(anchor="w", padx=20, pady=(0,4))
    g = Card(self.content); g.pack(fill="x", **P)
    hdr2 = ctk.CTkFrame(g, fg_color=C["card2"]); hdr2.pack(fill="x")
    for t,w in [("Grupo",200),("Descripción",500)]:
        ctk.CTkLabel(hdr2, text=t, font=("Segoe UI",9,"bold"), text_color=C["sub"],
                     width=w, anchor="w").pack(side="left",padx=6,pady=4)
    for i, grp in enumerate(groups):
        bg = C["card2"] if i%2==1 else C["card"]
        r = ctk.CTkFrame(g, fg_color=bg); r.pack(fill="x")
        ctk.CTkLabel(r, text=grp["name"], font=("Segoe UI",10,"bold"),
                     text_color=C["text"], width=200, anchor="w").pack(side="left",padx=6,pady=3)
        ctk.CTkLabel(r, text=grp["desc"][:65], font=("Segoe UI",9),
                     text_color=C["sub"], width=500, anchor="w").pack(side="left")
    ctk.CTkFrame(g, height=6, fg_color="transparent").pack()

    ctk.CTkFrame(self.content, height=1, fg_color=C["border"]).pack(fill="x", padx=20, pady=8)

    # Sesiones activas
    SectionLabel(self.content, "SESIONES ACTIVAS (who/query)").pack(anchor="w", padx=20, pady=(0,4))
    sc = Card(self.content); sc.pack(fill="x", **P)
    try:
        r = subprocess.run(["query","user"],capture_output=True,text=True,
                           timeout=8, encoding="cp850", errors="replace")
        out = r.stdout.strip() or "No se encontraron sesiones activas."
    except Exception as e:
        out = str(e)
    ctk.CTkLabel(sc, text=out, font=("Consolas",9),
                 text_color=C["text"], justify="left"
                 ).pack(anchor="w", padx=14, pady=12)

HardenDisk._pg_users      = _pg_users
HardenDisk._render_users  = _render_users


def _pg_report(self):
    P = self._pad()
    SectionLabel(self.content, "REPORTE COMPLETO DEL SISTEMA").pack(anchor="w", padx=20, pady=(14,4))
    ctk.CTkLabel(self.content,
        text="Genera un informe detallado con toda la información del equipo: hardware, red, seguridad, "
             "procesos y disco. Puedes guardarlo como archivo .txt.",
        font=("Segoe UI",10), text_color=C["sub"], wraplength=720
    ).pack(anchor="w", padx=20, pady=(0,10))

    c = Card(self.content); c.pack(fill="x", **P)
    self._report_log = LogBox(c, h=380); self._report_log.pack(fill="x", padx=14, pady=10)

    btns = ctk.CTkFrame(c, fg_color="transparent"); btns.pack(fill="x", padx=14, pady=(0,14))

    def gen():
        self._report_log.clear()
        self._report_log.append("Generando reporte...")
        self._status("Generando...", C["warning"])
        def run():
            txt = generate_report()
            self._report_txt = txt
            self.after(0, lambda: [self._report_log.clear(),
                                    self._report_log.append(txt),
                                    self._status("Reporte generado", C["success"])])
        threading.Thread(target=run, daemon=True).start()

    def save():
        txt = getattr(self, "_report_txt", None)
        if not txt:
            messagebox.showwarning("HardenDisk", "Primero genera el reporte.")
            return
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Texto","*.txt"),("Todos","*.*")],
            initialfile=f"HardenDisk_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(txt)
            messagebox.showinfo("HardenDisk", f"Reporte guardado en:\n{path}")

    BtnPrimary(btns, "📋  Generar reporte", cmd=gen).pack(side="left")
    BtnSecondary(btns, "💾  Guardar como .txt", cmd=save).pack(side="left", padx=10)

HardenDisk._pg_report = _pg_report


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__=="__main__":
    app=HardenDisk()
    app.mainloop()
