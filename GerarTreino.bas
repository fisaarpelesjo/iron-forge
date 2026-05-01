Sub GerarTreino()
    Dim oDoc As Object
    Dim oTreinos As Object
    Dim oExercicios As Object
    Dim treino As String
    Dim startEx As Integer
    Dim endEx As Integer
    Dim i As Integer
    Dim cursor As Object
    Dim lastRow As Long
    Dim newRow As Long
    Dim oCell As Object
    Dim r As Long
    Dim nFormat As Long
    Dim oFormats As Object
    Dim oLocale As New com.sun.star.lang.Locale
    oLocale.Language = "pt"
    oLocale.Country = "BR"

    oDoc = ThisComponent
    oTreinos = oDoc.Sheets.getByName("TREINOS")
    oExercicios = oDoc.Sheets.getByName("EXERCICIOS")

    treino = InputBox("Qual treino deseja registrar?" & Chr(10) & "Digite A, B ou C:", "Gerar Treino", "A")
    If treino = "" Then Exit Sub
    treino = UCase(Trim(treino))

    If treino = "A" Then
        startEx = 0
        endEx = 7
    ElseIf treino = "B" Then
        startEx = 8
        endEx = 14
    ElseIf treino = "C" Then
        startEx = 15
        endEx = 17
    Else
        MsgBox "Treino invalido. Digite A, B ou C.", 16, "Erro"
        Exit Sub
    End If

    cursor = oTreinos.createCursor()
    cursor.gotoEndOfUsedArea(True)
    lastRow = cursor.getRangeAddress().EndRow

    oFormats = oDoc.getNumberFormats()
    nFormat = oFormats.queryKey("DD/MM/YYYY", oLocale, False)
    If nFormat = -1 Then
        nFormat = oFormats.addNew("DD/MM/YYYY", oLocale)
    End If

    For i = startEx To endEx
        newRow = lastRow + 1 + (i - startEx)
        r = newRow + 1

        oCell = oTreinos.getCellByPosition(0, newRow)
        oCell.setValue(Now())
        oCell.NumberFormat = nFormat

        oTreinos.getCellByPosition(1, newRow).setFormula( _
            "=IF(A" & r & "="""";"""";YEAR(A" & r & ")&""-W""&TEXT(ISOWEEKNUM(A" & r & ");""00""))")

        oTreinos.getCellByPosition(2, newRow).setString(treino)

        oTreinos.getCellByPosition(3, newRow).setString( _
            oExercicios.getCellByPosition(0, i).getString())

        oTreinos.getCellByPosition(4, newRow).setValue( _
            oExercicios.getCellByPosition(1, i).getValue())

        oTreinos.getCellByPosition(5, newRow).setValue( _
            oExercicios.getCellByPosition(2, i).getValue())

        oTreinos.getCellByPosition(8, newRow).setFormula( _
            "=IFERROR(E" & r & "*F" & r & "*G" & r & ";0)")

        oTreinos.getCellByPosition(9, newRow).setFormula( _
            "=IF(H" & r & "="""";"""";IF(H" & r & "<=8;""AUMENTAR"";IF(H" & r & "=9;""MANTER"";""REDUZIR"")))")

        oTreinos.getCellByPosition(10, newRow).setFormula( _
            "=IF(ROW()=2;"""";IFERROR(LOOKUP(2;1/($D$2:INDEX($D:$D;ROW()-1)=D" & r & ");$G$2:INDEX($G:$G;ROW()-1));""""))")

        oTreinos.getCellByPosition(11, newRow).setFormula( _
            "=IF(J" & r & "=""AUMENTAR"";G" & r & "+2.5;IF(J" & r & "=""REDUZIR"";G" & r & "-2.5;G" & r & "))")
    Next i

    Dim oCFRange As Object
    oCFRange = oTreinos.getCellRangeByPosition(3, 1, 12, newRow)
    oCFRange.CellBackColor = -1

    Dim oNewCF As Object
    oNewCF = oCFRange.ConditionalFormat
    oNewCF.clear()

    Dim aProps(2) As New com.sun.star.beans.PropertyValue
    aProps(0).Name = "Operator"
    aProps(0).Value = com.sun.star.sheet.ConditionOperator.FORMULA
    aProps(1).Name = "Formula1"
    aProps(2).Name = "StyleName"

    aProps(1).Value = "$J1=""AUMENTAR"""
    aProps(2).Value = "ConditionalStyle_2"
    oNewCF.addNew(aProps())

    aProps(1).Value = "$J1=""REDUZIR"""
    aProps(2).Value = "ConditionalStyle_3"
    oNewCF.addNew(aProps())

    aProps(1).Value = "$J1=""MANTER"""
    aProps(2).Value = "ConditionalStyle_4"
    oNewCF.addNew(aProps())

    oCFRange.ConditionalFormat = oNewCF

    Dim oABRange As Object
    oABRange = oTreinos.getCellRangeByPosition(0, 1, 1, newRow)
    oABRange.CellBackColor = -1

    Dim oABCF As Object
    oABCF = oABRange.ConditionalFormat
    oABCF.clear()

    aProps(1).Value = "$A1<>$A0"
    aProps(2).Value = "ConditionalStyle_1"
    oABCF.addNew(aProps())

    oABRange.ConditionalFormat = oABCF

    MsgBox "Treino " & treino & " gerado! " & (endEx - startEx + 1) & _
           " exercicios adicionados a partir da linha " & (lastRow + 2) & ".", _
           64, "Treino Gerado"

    ' Send Telegram notification
    Dim sBotToken As String
    sBotToken = LerTokenTelegram()
    If sBotToken <> "" Then
        Dim sMsg As String
        sMsg = "Treino " & treino & " — " & Format(Now(), "DD/MM/YYYY") & Chr(10) & Chr(10)
        Dim j As Integer
        For j = startEx To endEx
            sMsg = sMsg & "- " & oExercicios.getCellByPosition(0, j).getString() & _
                ": " & CInt(oExercicios.getCellByPosition(1, j).getValue()) & "x" & _
                CInt(oExercicios.getCellByPosition(2, j).getValue()) & Chr(10)
        Next j
        EnviarTelegram sBotToken, "6575275306", sMsg
    End If

    Dim oRange As Object
    oRange = oTreinos.getCellByPosition(0, lastRow + 1)
    oDoc.getCurrentController().setActiveSheet(oTreinos)
    oDoc.getCurrentController().select(oRange)
End Sub

Function LerTokenTelegram() As String
    Dim sDocURL As String
    Dim sDir As String
    Dim sEnvPath As String

    sDocURL = ThisComponent.getURL()
    sDir = Left(sDocURL, InStrRev(sDocURL, "/"))
    sEnvPath = ConvertFromURL(sDir & ".env")

    Dim iFile As Integer
    Dim sLine As String
    Dim eqPos As Integer
    iFile = FreeFile()

    On Error GoTo ErrorHandler
    Open sEnvPath For Input As #iFile
    Do While Not EOF(iFile)
        Line Input #iFile, sLine
        sLine = Trim(sLine)
        eqPos = InStr(sLine, "=")
        If eqPos > 0 Then
            If UCase(Left(sLine, eqPos - 1)) = "TELEGRAM_TOKEN" Then
                Close #iFile
                LerTokenTelegram = Mid(sLine, eqPos + 1)
                Exit Function
            End If
        End If
    Loop
    Close #iFile
    LerTokenTelegram = ""
    Exit Function
ErrorHandler:
    LerTokenTelegram = ""
End Function

Sub EnviarTelegram(ByVal sBotToken As String, ByVal sChatId As String, ByVal sMsg As String)
    Dim sTempFile As String
    sTempFile = Environ("TEMP") & "\ironforge_msg.txt"

    Dim iFile As Integer
    iFile = FreeFile()
    Open sTempFile For Output As #iFile
    Print #iFile, sMsg
    Close #iFile

    Dim sPS As String
    sPS = "$msg = (Get-Content '" & sTempFile & "' -Raw -Encoding UTF8).Trim();" & _
          "Invoke-RestMethod -Uri 'https://api.telegram.org/bot" & sBotToken & "/sendMessage'" & _
          " -Method Post -Body @{chat_id='" & sChatId & "';text=$msg} | Out-Null;" & _
          "Remove-Item '" & sTempFile & "'"

    Shell "powershell.exe", 0, "-WindowStyle Hidden -NonInteractive -Command " & Chr(34) & sPS & Chr(34), False
End Sub
